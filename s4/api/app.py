"""API server for S4 service."""

import io
import logging
import mimetypes
import os
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from s4 import config
from s4.api.models import (
    FileMetadata, FileInfo, SearchRequest, SearchResponse, 
    UpdateMetadataRequest, BasicResponse, FileUploadResponse, SearchResult
)
from s4.service import S4Service

# Validate configuration before starting
config.validate_config()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="S4 API",
    description="S4 - Smart S3 Storage Service API",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service dependency
def get_s4_service():
    """Dependency to get S4 service instance."""
    return S4Service()

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {"message": "Welcome to S4 API", "docs": "/docs"}

@app.post("/files/", response_model=FileUploadResponse, tags=["Files"])
async def upload_file(
    file: UploadFile = File(...),
    index: bool = Form(True),
    metadata: Optional[str] = Form(None),
    s4_service: S4Service = Depends(get_s4_service),
):
    """Upload a file to S3 and optionally index it.
    
    - **file**: The file to upload
    - **index**: Whether to index the file for search (default: True)
    - **metadata**: Optional JSON string with metadata key-value pairs
    """
    try:
        # Get file content
        file_content = await file.read()
        
        # Parse custom metadata if provided
        custom_metadata = {}
        if metadata:
            try:
                import json
                custom_metadata = json.loads(metadata)
                if not isinstance(custom_metadata, dict):
                    raise HTTPException(status_code=400, detail="Metadata must be a JSON object")
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in metadata")
                
        # Determine content type
        content_type = file.content_type
        if not content_type:
            content_type, _ = mimetypes.guess_type(file.filename)
            
        # Upload file to S3 with indexing
        file_info = s4_service.upload_file(
            file_obj=file_content,
            file_name=file.filename,
            content_type=content_type,
            metadata=custom_metadata,
            index=index
        )
        
        # Create response
        return FileUploadResponse(
            file_id=file_info["file_id"],
            file_name=file_info["file_name"],
            content_type=file_info["content_type"],
            indexed=file_info["indexed"],
            metadata=file_info["metadata"],
        )
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/files/", response_model=List[FileInfo], tags=["Files"])
async def list_files(
    prefix: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    s4_service: S4Service = Depends(get_s4_service),
):
    """List files in the S3 bucket.
    
    - **prefix**: Optional prefix to filter files
    - **limit**: Maximum number of files to return (default: 100, max: 1000)
    """
    try:
        files = s4_service.list_files(prefix=prefix, max_files=limit)
        return files
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.get("/files/{file_id}", tags=["Files"])
async def download_file(
    file_id: str,
    s4_service: S4Service = Depends(get_s4_service),
):
    """Download a file from S3.
    
    - **file_id**: ID of the file to download
    """
    try:
        file_content, metadata = s4_service.download_file(file_id)
        
        # Get filename and content type from metadata if available
        filename = metadata.get("filename", file_id.split("/")[-1] if "/" in file_id else file_id)
        content_type = metadata.get("content-type", "application/octet-stream")
        
        # Set content disposition header to suggest filename
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(file_content.getvalue()),
            media_type=content_type,
            headers=headers
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found")
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@app.delete("/files/{file_id}", response_model=BasicResponse, tags=["Files"])
async def delete_file(
    file_id: str,
    remove_from_index: bool = True,
    s4_service: S4Service = Depends(get_s4_service),
):
    """Delete a file from S3 and optionally from the index.
    
    - **file_id**: ID of the file to delete
    - **remove_from_index**: Whether to also remove from index (default: True)
    """
    try:
        success = s4_service.delete_file(file_id, remove_from_index=remove_from_index)
        return BasicResponse(
            success=success,
            message=f"File {file_id} deleted successfully"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.post("/search/", response_model=SearchResponse, tags=["Search"])
async def search(
    search_request: SearchRequest,
    s4_service: S4Service = Depends(get_s4_service),
):
    """Search indexed documents using semantic search.
    
    - **query**: Search query
    - **limit**: Maximum number of results (default: 5)
    - **file_id**: Optional file ID to restrict search to
    """
    try:
        results = s4_service.search(
            query=search_request.query,
            limit=search_request.limit or 5,
            file_id=search_request.file_id
        )
        
        # Convert to response model
        search_results = [
            SearchResult(
                content=r["content"],
                score=r["score"],
                metadata=r["metadata"]
            ) for r in results
        ]
        
        return SearchResponse(
            results=search_results,
            query=search_request.query,
            total_results=len(search_results)
        )
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

@app.put("/files/{file_id}/metadata", response_model=BasicResponse, tags=["Files"])
async def update_metadata(
    file_id: str,
    metadata_request: UpdateMetadataRequest,
    s4_service: S4Service = Depends(get_s4_service),
):
    """Update metadata for a file.
    
    - **file_id**: ID of the file
    - **metadata**: New metadata to merge with existing
    """
    try:
        success = s4_service.update_metadata(file_id, metadata_request.metadata)
        return BasicResponse(
            success=success,
            message=f"Metadata for file {file_id} updated successfully"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found")
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating metadata: {str(e)}")

def run_server():
    """Run the API server."""
    uvicorn.run(
        "s4.api.app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )

if __name__ == "__main__":
    run_server() 