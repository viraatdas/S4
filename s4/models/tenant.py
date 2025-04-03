"""Tenant models for S4 SaaS."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, validator


class PlanType:
    """Available subscription plans."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class Plan(BaseModel):
    """Subscription plan model."""
    id: str
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    storage_limit_gb: float  # Storage limit in GB
    monthly_requests: int  # API requests per month
    max_file_size_mb: int  # Maximum file size in MB
    features: List[str]  # List of enabled features


class Tenant(BaseModel):
    """Tenant model for multi-tenant support."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
    
    # Authentication information
    auth_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Account information
    email: str
    company: Optional[str] = None
    
    # Subscription information
    plan: str = PlanType.FREE
    plan_expires_at: Optional[datetime] = None
    
    # Usage metrics
    storage_used_bytes: int = 0
    api_requests_count: int = 0
    file_count: int = 0
    
    # Custom configuration
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    openai_api_key: Optional[str] = None
    custom_bucket_name: Optional[str] = None  # Legacy field, keeping for compatibility
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None  # Legacy field, keeping for compatibility
    
    # Feature flags
    features: Dict[str, bool] = Field(default_factory=dict)
    
    @validator('auth_key', pre=True, always=True)
    def set_auth_key(cls, v):
        """Ensure auth_key is set."""
        if not v:
            return str(uuid.uuid4())
        return v
    
    def increment_usage(self, file_size: int = 0, api_requests: int = 1):
        """Increment usage metrics.
        
        Args:
            file_size: Size of file in bytes
            api_requests: Number of API requests
        """
        self.storage_used_bytes += file_size
        self.api_requests_count += api_requests
        if file_size > 0:
            self.file_count += 1
    
    def check_storage_limit(self, additional_bytes: int = 0) -> bool:
        """Check if tenant is within storage limits.
        
        Args:
            additional_bytes: Additional bytes to check
            
        Returns:
            bool: True if within limits
        """
        # Convert GB to bytes for comparison (1 GB = 1073741824 bytes)
        plans = get_plans()
        plan = next((p for p in plans if p.id == self.plan), None)
        
        if not plan:
            return False
            
        storage_limit_bytes = plan.storage_limit_gb * 1073741824
        return (self.storage_used_bytes + additional_bytes) <= storage_limit_bytes
    
    def check_api_limit(self) -> bool:
        """Check if tenant is within API request limits.
        
        Returns:
            bool: True if within limits
        """
        plans = get_plans()
        plan = next((p for p in plans if p.id == self.plan), None)
        
        if not plan:
            return False
            
        return self.api_requests_count <= plan.monthly_requests
        
    def check_file_size_limit(self, file_size_bytes: int) -> bool:
        """Check if file size is within limits.
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            bool: True if within limits
        """
        plans = get_plans()
        plan = next((p for p in plans if p.id == self.plan), None)
        
        if not plan:
            return False
            
        # Convert MB to bytes for comparison (1 MB = 1048576 bytes)
        max_size_bytes = plan.max_file_size_mb * 1048576
        return file_size_bytes <= max_size_bytes
    
    def get_s3_config(self) -> Dict[str, str]:
        """Get S3 configuration for tenant.
        
        Returns:
            Dict with S3 configuration
        """
        # Use tenant-specific config if available, otherwise use default
        return {
            "aws_access_key_id": self.aws_access_key_id or None,
            "aws_secret_access_key": self.aws_secret_access_key or None,
            "aws_region": self.s3_region or self.aws_region or None,
            "bucket_name": self.s3_bucket or self.custom_bucket_name or None
        }

    def get_plan_object(self) -> Plan:
        """Get the Plan object for this tenant.
        
        Returns:
            Plan object corresponding to the plan ID
        """
        plans = {p.id: p for p in get_plans()}
        return plans.get(self.plan, plans[PlanType.FREE])


def get_plans() -> List[Plan]:
    """Get available subscription plans.
    
    Returns:
        List of plan objects
    """
    return [
        Plan(
            id=PlanType.FREE,
            name="Free",
            description="Basic access for individuals",
            price_monthly=0,
            price_yearly=0,
            storage_limit_gb=1,
            monthly_requests=100,
            max_file_size_mb=10,
            features=["Basic search", "PDF indexing", "Text indexing"]
        ),
        Plan(
            id=PlanType.BASIC,
            name="Basic",
            description="For small teams and projects",
            price_monthly=29,
            price_yearly=299,
            storage_limit_gb=10,
            monthly_requests=1000,
            max_file_size_mb=50,
            features=["Basic search", "PDF indexing", "Text indexing", "Word indexing", "Excel indexing"]
        ),
        Plan(
            id=PlanType.PREMIUM,
            name="Premium",
            description="For growing businesses",
            price_monthly=99,
            price_yearly=999,
            storage_limit_gb=50,
            monthly_requests=10000,
            max_file_size_mb=200,
            features=["Advanced search", "PDF indexing", "Text indexing", "Word indexing", 
                      "Excel indexing", "JSON indexing", "YAML indexing", "API access"]
        ),
        Plan(
            id=PlanType.ENTERPRISE,
            name="Enterprise",
            description="For large organizations",
            price_monthly=499,
            price_yearly=4999,
            storage_limit_gb=500,
            monthly_requests=100000,
            max_file_size_mb=1000,
            features=["Advanced search", "All file types", "API access", 
                      "Custom S3 bucket", "Custom integrations", "SLA", "Dedicated support"]
        )
    ] 