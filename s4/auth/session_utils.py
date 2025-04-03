"""Utilities for bridging SuperTokens sessions with S4 API authentication."""

import logging
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from s4.db import tenant_manager
from s4.service import S4Service

logger = logging.getLogger(__name__)


async def get_tenant_id_from_session(session: SessionContainer) -> Optional[str]:
    """Get tenant ID from a SuperTokens session.
    
    Args:
        session: SuperTokens session container
        
    Returns:
        Tenant ID or None if not found
    """
    try:
        user_id = session.get_user_id()
        user_info = await session.get_session_data()
        email = user_info.get("email")
        
        if not email:
            # Try to get email from user info
            from supertokens_python.recipe.thirdparty.asyncio import get_user_by_id
            user = await get_user_by_id(user_id)
            if user:
                email = user.email
        
        if email:
            # Get tenant by email
            tenant = tenant_manager.get_tenant_by_email(email)
            if tenant:
                return tenant.id
    
    except Exception as e:
        logger.error(f"Error getting tenant ID from session: {e}")
    
    return None


async def get_s4_service_from_session(session: SessionContainer = Depends(verify_session())) -> S4Service:
    """Get S4 service for the authenticated user.
    
    Args:
        session: SuperTokens session container
        
    Returns:
        S4Service instance for the authenticated tenant
    """
    tenant_id = await get_tenant_id_from_session(session)
    
    if not tenant_id:
        raise HTTPException(status_code=403, detail="No tenant associated with this account")
    
    try:
        return S4Service(tenant_id=tenant_id)
    except Exception as e:
        logger.error(f"Error initializing S4 service: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Combined auth dependency that works with both SuperTokens and API key auth
async def get_s4_service(request: Request) -> S4Service:
    """Get S4 service using either SuperTokens session or API key.
    
    This allows for a smooth transition from API key auth to SuperTokens.
    
    Args:
        request: FastAPI request object
        
    Returns:
        S4Service instance for the authenticated tenant
    """
    from s4.api.routes import verify_auth_key, get_s4_service as api_key_get_s4_service
    
    # First try SuperTokens session
    try:
        session = await verify_session()(request)
        return await get_s4_service_from_session(session)
    except Exception as e:
        # If SuperTokens auth fails, fall back to API key auth
        logger.debug(f"SuperTokens auth failed, trying API key: {e}")
        
        # Get API key from header
        auth_key = request.headers.get("X-API-Key")
        if not auth_key:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Verify API key and get tenant ID
        tenant_id = await verify_auth_key(auth_key)
        
        # Get S4 service
        return await api_key_get_s4_service(tenant_id)
