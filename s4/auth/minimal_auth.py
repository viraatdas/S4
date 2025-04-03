"""Authentication module for S4 that handles both API key and SuperTokens authentication."""

import logging
from typing import Optional, Union, Dict, Any

from fastapi import Request, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from s4.db import tenant_manager
from s4.service import S4Service
from s4.exceptions import ValidationError

# Setup logging
logger = logging.getLogger(__name__)

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_tenant_id(request: Request, api_key: str = Depends(API_KEY_HEADER), authorization: Optional[str] = Header(None)):
    """Get tenant ID from API key or SuperTokens session.
    
    Args:
        request: FastAPI request object
        api_key: API key from X-API-Key header
        authorization: Authorization header for SuperTokens session
        
    Returns:
        Tenant ID if authentication is successful
        
    Raises:
        HTTPException: If authentication fails
    """
    # First try API key authentication
    if api_key:
        try:
            tenant = tenant_manager.get_tenant_by_auth_key(api_key)
            if not tenant:
                raise HTTPException(status_code=401, detail="Invalid API key")
            if not tenant.active:
                raise HTTPException(status_code=403, detail="Tenant account is inactive")
            logger.info(f"Authenticated tenant {tenant.id} using API key")
            return tenant.id
        except Exception as e:
            logger.error(f"API key authentication error: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
    
    # If no API key, try SuperTokens session
    if authorization and authorization.startswith("Bearer "):
        try:
            # In a real implementation, you would verify the SuperTokens session here
            # For now, we'll extract user info from the request context if available
            user_id = request.state.user_id if hasattr(request.state, "user_id") else None
            if user_id:
                # Look up tenant by user ID
                tenant = tenant_manager.get_tenant_by_user_id(user_id)
                if tenant:
                    logger.info(f"Authenticated tenant {tenant.id} using SuperTokens session")
                    return tenant.id
            
            # If we can't find a tenant, authentication failed
            raise HTTPException(status_code=401, detail="Invalid session or user not associated with a tenant")
        except Exception as e:
            logger.error(f"SuperTokens authentication error: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
    
    # If no authentication method provided
    raise HTTPException(status_code=401, detail="Authentication required (API key or session)")

async def get_s4_service(request: Request):
    """Get S4 service for the authenticated tenant.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Initialized S4Service instance for the authenticated tenant
        
    Raises:
        HTTPException: If authentication fails or service initialization fails
    """
    try:
        tenant_id = await get_tenant_id(request)
        return S4Service(tenant_id=tenant_id)
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"S4Service validation error: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing S4 service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
