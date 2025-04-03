"""API routes for S4."""

import io
import logging
import tempfile
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Header, UploadFile, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from s4 import config
from s4.service import S4Service
from s4.exceptions import S4Error, ValidationError
from s4.db import tenant_manager
from s4.auth.minimal_auth import get_s4_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Models for request/response
class FileMetadata(BaseModel):
    """Metadata for a file."""
    
    file_id: str
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME type")
    uploaded_at: Optional[str] = Field(None, description="Upload timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")

class SearchResult(BaseModel):
    """Search result."""
    
    content: str = Field(..., description="Content snippet")
    score: float = Field(..., description="Search score")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    file_metadata: Optional[Dict[str, Any]] = Field(None, description="File metadata")

class TenantUsage(BaseModel):
    """Tenant usage statistics."""
    
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_used_percentage: float
    api_requests_count: int
    api_requests_limit: int
    api_requests_percentage: float
    file_count: int
    plan: Dict[str, Any]

# Authentication dependency
async def verify_auth_key(x_auth_key: str = Header(None)) -> str:
    """Verify authentication key and return tenant ID."""
    if not x_auth_key:
        raise HTTPException(status_code=401, detail="Authentication key required")
        
    # Allow anonymous access (no tenant) if API auth is disabled
    if config.DISABLE_API_AUTH and x_auth_key == config.DEFAULT_API_KEY:
        return None
        
    # Look up tenant by auth key
    tenant = tenant_manager.get_tenant_by_auth_key(x_auth_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid authentication key")
        
    if not tenant.active:
        raise HTTPException(status_code=403, detail="Tenant account is inactive")
        
    return tenant.id

# Dependency for getting S4 service with tenant info
async def get_s4_service(tenant_id: str = Depends(verify_auth_key)) -> S4Service:
    """Get S4 service for the authenticated tenant."""
    try:
        return S4Service(tenant_id=tenant_id)
    except ValidationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing S4 service: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Use minimal auth dependency that only uses API key auth
async def get_s4_service_combined(request: Request) -> S4Service:
    """Get S4 service using API key authentication.
    """
    return await get_s4_service(request)

@router.post("/files", response_model=FileMetadata)
async def upload_file(
    file: UploadFile = File(...),
    file_id: Optional[str] = Form(None),
    metadata_json: Optional[str] = Form(None),
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """Upload a file to S4."""
    try:
        # Parse metadata if provided
        metadata = {}
        if metadata_json:
            import json
            metadata = json.loads(metadata_json)
            
        # Read file content
        file_content = await file.read()
        
        # Upload file
        file_id = s4_service.upload_file_object(
            io.BytesIO(file_content),
            filename=file.filename,
            content_type=file.content_type,
            file_id=file_id,
            metadata=metadata
        )
        
        # Get file metadata
        result = s4_service.get_file_metadata(file_id)
        
        return result
    except S4Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files/{file_id}", response_class=StreamingResponse)
async def download_file(
    file_id: str,
    disposition: str = "attachment",
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """Download a file from S4."""
    try:
        # Get file metadata for content type
        metadata = s4_service.get_file_metadata(file_id)
        
        # Download to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
        file_path = s4_service.download_file(file_id, temp_path)
        
        # Get filename from metadata
        filename = metadata.get("original_filename", file_id)
        
        # Return streaming response
        def file_generator():
            with open(file_path, "rb") as f:
                yield from f
            # Clean up temp file after streaming
            Path(file_path).unlink(missing_ok=True)
            
        headers = {}
        if disposition == "inline":
            headers["Content-Disposition"] = f"inline; filename=\"{filename}\""
        else:
            headers["Content-Disposition"] = f"attachment; filename=\"{filename}\""
            
        if "content_type" in metadata:
            return StreamingResponse(
                file_generator(), 
                media_type=metadata["content_type"],
                headers=headers
            )
        return StreamingResponse(
            file_generator(),
            headers=headers
        )
    except S4Error as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error downloading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """Delete a file from S4."""
    try:
        s4_service.delete_file(file_id)
        return {"status": "success", "message": f"File {file_id} deleted"}
    except S4Error as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files", response_model=List[FileMetadata])
async def list_files(
    prefix: str = "",
    max_results: int = 1000,
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """List files in S4."""
    try:
        result = s4_service.list_files(prefix, max_results)
        return result
    except S4Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=List[SearchResult])
async def search_files(
    query: str,
    limit: int = 5,
    file_id: Optional[str] = None,
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """Search for files in S4."""
    try:
        result = s4_service.search_files(query, limit, file_id)
        return result
    except S4Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error searching files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """Get metadata for a file."""
    try:
        result = s4_service.get_file_metadata(file_id)
        return result
    except S4Error as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting file metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/files/{file_id}/metadata", response_model=FileMetadata)
async def update_file_metadata(
    file_id: str,
    metadata: Dict[str, Any],
    s4_service: S4Service = Depends(get_s4_service_combined)
):
    """Update metadata for a file."""
    try:
        result = s4_service.update_file_metadata(file_id, metadata)
        return result
    except S4Error as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating file metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/usage", response_model=TenantUsage)
async def get_usage(s4_service: S4Service = Depends(get_s4_service_combined)):
    """Get tenant usage statistics."""
    try:
        usage = s4_service.get_tenant_usage()
        if not usage:
            raise HTTPException(status_code=404, detail="Usage statistics not available")
        return usage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting usage statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 