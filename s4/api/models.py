"""API models for S4."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

class FileMetadata(BaseModel):
    """File metadata model."""
    file_name: Optional[str] = None
    content_type: Optional[str] = None
    custom_metadata: Optional[Dict[str, str]] = Field(default_factory=dict)

class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    file_id: str
    file_name: Optional[str] = None
    content_type: Optional[str] = None
    indexed: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)
    upload_time: datetime = Field(default_factory=datetime.utcnow)

class FileInfo(BaseModel):
    """File information model."""
    id: str
    size: int
    last_modified: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    indexed: bool = False
    index_metadata: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    """Search result model."""
    content: str
    score: float
    metadata: Dict[str, Any]

class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    limit: Optional[int] = 5
    file_id: Optional[str] = None

class SearchResponse(BaseModel):
    """Search response model."""
    results: List[SearchResult]
    query: str
    total_results: int

class UpdateMetadataRequest(BaseModel):
    """Update metadata request model."""
    metadata: Dict[str, str]

class BasicResponse(BaseModel):
    """Basic response model."""
    success: bool
    message: str 