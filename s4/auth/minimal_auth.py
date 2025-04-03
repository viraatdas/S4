"""Minimal authentication module for S4 that doesn't rely on SuperTokens."""

from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from s4.db import tenant_manager
from s4.service import S4Service

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_tenant_id(request: Request, api_key: str = Depends(API_KEY_HEADER)):
    """Get tenant ID from API key."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify API key and get tenant ID
    try:
        tenant = tenant_manager.get_tenant_by_auth_key(api_key)
        if not tenant:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return tenant.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

async def get_s4_service(request: Request):
    """Get S4 service for the authenticated tenant."""
    tenant_id = await get_tenant_id(request)
    return S4Service(tenant_id=tenant_id)
