"""Tenant manager for multi-tenant support."""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import secrets

from s4 import config
from s4.models import Tenant, PlanType

logger = logging.getLogger(__name__)

# Path for tenant data storage
TENANT_DATA_PATH = Path(config.DATA_DIR) / "tenants"
TENANT_DATA_PATH.mkdir(parents=True, exist_ok=True)


class TenantManager:
    """Manager for tenant operations."""
    
    def __init__(self):
        """Initialize tenant manager."""
        self.tenants = self._load_tenants()
        
    def _load_tenants(self) -> Dict[str, Tenant]:
        """Load tenants from storage.
        
        Returns:
            Dict of tenant ID to Tenant object
        """
        tenants = {}
        
        # Ensure directory exists
        if not TENANT_DATA_PATH.exists():
            TENANT_DATA_PATH.mkdir(parents=True, exist_ok=True)
            return tenants
            
        # Load each tenant file
        for tenant_file in TENANT_DATA_PATH.glob("*.json"):
            try:
                with open(tenant_file, "r") as f:
                    tenant_data = json.load(f)
                    tenant = Tenant(**tenant_data)
                    tenants[tenant.id] = tenant
            except Exception as e:
                logger.error(f"Error loading tenant from {tenant_file}: {e}")
                
        return tenants
    
    def _save_tenant(self, tenant: Tenant):
        """Save tenant to storage.
        
        Args:
            tenant: Tenant to save
        """
        tenant_file = TENANT_DATA_PATH / f"{tenant.id}.json"
        
        try:
            with open(tenant_file, "w") as f:
                json.dump(tenant.dict(), f, default=str)
        except Exception as e:
            logger.error(f"Error saving tenant {tenant.id}: {e}")
            
    def create_tenant(
        self, 
        name: str, 
        email: str, 
        company: Optional[str] = None,
        plan_id: str = "free",
        auth_key: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_region: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        active: bool = True,
        plan_expires_at: Optional[datetime] = None
    ) -> Tenant:
        """Create a new tenant.
        
        Args:
            name: Tenant name
            email: Contact email
            company: Company name (optional)
            plan_id: Subscription plan ID
            auth_key: Authentication key (optional, will be generated if not provided)
            s3_bucket: Custom S3 bucket (optional)
            s3_region: Custom S3 region (optional)
            openai_api_key: Custom OpenAI API key (optional)
            active: Whether the tenant is active (default True)
            plan_expires_at: When the plan expires (default 30 days)
            
        Returns:
            Newly created Tenant
        """
        # Generate auth key if not provided
        if not auth_key:
            auth_key = f"s4_{secrets.token_urlsafe(16)}"
            
        # Set default plan expiration if not provided
        if not plan_expires_at:
            plan_expires_at = (
                datetime.utcnow() + timedelta(days=30)
                if plan_id != "free" else None
            )
        
        # Create tenant
        tenant = Tenant(
            name=name,
            email=email,
            company=company,
            plan=plan_id,  # Use plan_id as plan
            auth_key=auth_key,
            s3_bucket=s3_bucket,
            s3_region=s3_region,
            openai_api_key=openai_api_key,
            active=active,
            plan_expires_at=plan_expires_at
        )
        
        # Save tenant
        self.tenants[tenant.id] = tenant
        self._save_tenant(tenant)
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tenant object or None if not found
        """
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_auth_key(self, auth_key: str) -> Optional[Tenant]:
        """Get tenant by authentication key.
        
        Args:
            auth_key: Authentication key
            
        Returns:
            Tenant object or None if not found
        """
        for tenant in self.tenants.values():
            if tenant.auth_key == auth_key:
                return tenant
        return None
        
    def get_tenant_by_email(self, email: str) -> Optional[Tenant]:
        """Get tenant by email address.
        
        Args:
            email: Email address
            
        Returns:
            Tenant object or None if not found
        """
        for tenant in self.tenants.values():
            if tenant.email == email:
                return tenant
        return None
        
    def update_tenant(self, tenant: Tenant) -> bool:
        """Update tenant.
        
        Args:
            tenant: Tenant to update
            
        Returns:
            True if successful
        """
        if tenant.id not in self.tenants:
            return False
            
        self.tenants[tenant.id] = tenant
        self._save_tenant(tenant)
        
        return True
        
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if successful
        """
        if tenant_id not in self.tenants:
            return False
            
        tenant_file = TENANT_DATA_PATH / f"{tenant_id}.json"
        
        try:
            # Remove from memory
            del self.tenants[tenant_id]
            
            # Remove file
            if tenant_file.exists():
                os.remove(tenant_file)
                
            return True
        except Exception as e:
            logger.error(f"Error deleting tenant {tenant_id}: {e}")
            return False
            
    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants.
        
        Returns:
            List of all tenants
        """
        return list(self.tenants.values())
    
    def increment_tenant_usage(
        self, 
        tenant_id: str, 
        file_size: int = 0, 
        api_requests: int = 1
    ) -> bool:
        """Increment tenant usage metrics.
        
        Args:
            tenant_id: Tenant ID
            file_size: Size of file in bytes
            api_requests: Number of API requests
            
        Returns:
            True if successful
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
            
        tenant.increment_usage(file_size, api_requests)
        self._save_tenant(tenant)
        
        return True
        
    def check_tenant_limits(
        self,
        tenant_id: str,
        file_size: Optional[int] = None
    ) -> Dict[str, bool]:
        """Check if tenant is within limits.
        
        Args:
            tenant_id: Tenant ID
            file_size: Size of file to check
            
        Returns:
            Dict with limits status
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return {
                "active": False,
                "storage": False,
                "api": False,
                "file_size": False
            }
            
        result = {
            "active": tenant.active,
            "storage": True,
            "api": tenant.check_api_limit(),
            "file_size": True
        }
        
        # Check storage limit if adding a file
        if file_size is not None:
            result["storage"] = tenant.check_storage_limit(file_size)
            result["file_size"] = tenant.check_file_size_limit(file_size)
            
        return result 