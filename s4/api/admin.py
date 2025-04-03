"""Admin API routes for S4 (tenant management)."""

import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel, Field, EmailStr

from s4 import config
from s4.models import Tenant, Plan, PlanType, get_plans
from s4.db import tenant_manager
from s4.exceptions import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin API models
class TenantCreate(BaseModel):
    """Tenant creation request."""
    
    name: str = Field(..., description="Tenant name")
    email: EmailStr = Field(..., description="Admin email")
    company: Optional[str] = Field(None, description="Company name")
    plan_id: str = Field(..., description="Subscription plan ID")
    s3_bucket: Optional[str] = Field(None, description="Custom S3 bucket")
    s3_region: Optional[str] = Field(None, description="Custom S3 region")
    openai_api_key: Optional[str] = Field(None, description="Custom OpenAI API key")
    active: bool = Field(True, description="Whether the tenant is active")

class TenantUpdate(BaseModel):
    """Tenant update request."""
    
    name: Optional[str] = Field(None, description="Tenant name")
    email: Optional[EmailStr] = Field(None, description="Admin email")
    company: Optional[str] = Field(None, description="Company name")
    plan_id: Optional[str] = Field(None, description="Subscription plan ID")
    s3_bucket: Optional[str] = Field(None, description="Custom S3 bucket")
    s3_region: Optional[str] = Field(None, description="Custom S3 region")
    openai_api_key: Optional[str] = Field(None, description="Custom OpenAI API key")
    active: Optional[bool] = Field(None, description="Whether the tenant is active")
    plan_expires_at: Optional[datetime] = Field(None, description="When the plan expires")

class TenantResponse(BaseModel):
    """Tenant response model."""
    
    id: str
    name: str
    email: str
    company: Optional[str]
    created_at: datetime
    auth_key: str
    active: bool
    plan: Dict[str, Any]
    plan_expires_at: Optional[datetime]
    storage_used_bytes: int
    api_requests_count: int
    file_count: int
    s3_bucket: Optional[str]
    s3_region: Optional[str]
    
class PlanResponse(BaseModel):
    """Plan response model."""
    
    id: str
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    storage_limit_gb: int
    monthly_requests: int
    max_file_size_mb: int
    features: List[str]

# Admin authentication middleware
async def verify_admin_key(x_admin_key: str = Header(None)) -> None:
    """Verify admin authentication key."""
    if not x_admin_key:
        raise HTTPException(status_code=401, detail="Admin key required")
        
    if x_admin_key != config.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

# Plan endpoints
@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(_: None = Depends(verify_admin_key)):
    """List all available subscription plans."""
    return get_plans()

# Tenant management endpoints
@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    _: None = Depends(verify_admin_key)
):
    """Create a new tenant."""
    try:
        # Generate a secure auth key
        auth_key = f"s4_{secrets.token_urlsafe(32)}"
        
        # Set expiration date (default to 1 year)
        plan_expires_at = datetime.now() + timedelta(days=365)
        
        # Create the tenant
        tenant = tenant_manager.create_tenant(
            name=tenant_data.name,
            email=tenant_data.email,
            company=tenant_data.company,
            plan_id=tenant_data.plan_id,
            auth_key=auth_key,
            s3_bucket=tenant_data.s3_bucket,
            s3_region=tenant_data.s3_region,
            openai_api_key=tenant_data.openai_api_key,
            active=tenant_data.active,
            plan_expires_at=plan_expires_at
        )
        
        # Convert to response model
        result = tenant.dict()
        result['plan'] = tenant.get_plan_object().dict()
        
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(_: None = Depends(verify_admin_key)):
    """List all tenants."""
    try:
        tenants = tenant_manager.list_tenants()
        
        # Convert to response models
        results = []
        for tenant in tenants:
            result = tenant.dict()
            result['plan'] = tenant.get_plan_object().dict()
            results.append(result)
            
        return results
    except Exception as e:
        logger.error(f"Error listing tenants: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    _: None = Depends(verify_admin_key)
):
    """Get a tenant by ID."""
    try:
        tenant = tenant_manager.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
            
        # Convert to response model
        result = tenant.dict()
        result['plan'] = tenant.get_plan_object().dict()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    _: None = Depends(verify_admin_key)
):
    """Update a tenant."""
    try:
        # Check if tenant exists
        existing_tenant = tenant_manager.get_tenant(tenant_id)
        if not existing_tenant:
            raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
            
        # Build update dict with only provided fields
        update_data = tenant_data.dict(exclude_unset=True)
        
        # Update the tenant
        tenant = tenant_manager.update_tenant(tenant_id, update_data)
        
        # Convert to response model
        result = tenant.dict()
        result['plan'] = tenant.get_plan_object().dict()
        
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    _: None = Depends(verify_admin_key)
):
    """Delete a tenant."""
    try:
        # Check if tenant exists
        existing_tenant = tenant_manager.get_tenant(tenant_id)
        if not existing_tenant:
            raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
            
        # Delete the tenant
        tenant_manager.delete_tenant(tenant_id)
        
        return {"status": "success", "message": f"Tenant {tenant_id} deleted"}
    except Exception as e:
        logger.error(f"Error deleting tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/tenants/{tenant_id}/reset-key")
async def reset_tenant_key(
    tenant_id: str,
    _: None = Depends(verify_admin_key)
):
    """Reset a tenant's authentication key."""
    try:
        # Check if tenant exists
        existing_tenant = tenant_manager.get_tenant(tenant_id)
        if not existing_tenant:
            raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
            
        # Generate a new auth key
        new_auth_key = f"s4_{secrets.token_urlsafe(32)}"
        
        # Update the tenant with the new key
        tenant_manager.update_tenant(tenant_id, {"auth_key": new_auth_key})
        
        return {"status": "success", "auth_key": new_auth_key}
    except Exception as e:
        logger.error(f"Error resetting tenant key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 