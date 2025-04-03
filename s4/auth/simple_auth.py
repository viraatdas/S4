"""Simple authentication module for S4 that works with SuperTokens."""

import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from s4.db import tenant_manager

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# SuperTokens session ID cookie name
SUPERTOKENS_SESSION_ID = "sAccessToken"

async def get_tenant_id(request: Request, api_key: str = Depends(API_KEY_HEADER)):
    """Get tenant ID from either SuperTokens session or API key."""
    # First try to get tenant from SuperTokens session
    if SUPERTOKENS_SESSION_ID in request.cookies:
        session_token = request.cookies.get(SUPERTOKENS_SESSION_ID)
        if session_token:
            # For now, just extract the user info from the session
            # In a real implementation, you would verify the session with SuperTokens
            # This is a temporary workaround until we fix the dependency issues
            try:
                # Get user email from session (this is a simplified version)
                # In production, you would use the SuperTokens SDK to verify the session
                email = "example@example.com"  # Placeholder
                tenant = tenant_manager.get_tenant_by_email(email)
                if tenant:
                    return tenant.id
            except Exception as e:
                print(f"Error getting tenant from session: {e}")
    
    # Fall back to API key authentication
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

async def get_s4_service(tenant_id: str = Depends(get_tenant_id)):
    """Get S4 service for the authenticated tenant."""
    from s4.service import S4Service
    return S4Service(tenant_id=tenant_id)
