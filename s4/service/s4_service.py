"""Main S4 service that ties together storage and indexing."""

import io
import json
import logging
import mimetypes
from typing import Dict, List, Optional, Union, BinaryIO, Any, Tuple

from s4.storage import S3Storage
from s4.indexer import DocumentProcessor, DocumentIndex

logger = logging.getLogger(__name__)

class S4Service:
    """S4 service for intelligent file storage and retrieval."""
    
    def __init__(self, index_id: str = "default"):
        """Initialize the S4 service.
        
        Args:
            index_id: ID for the document index
        """
        self.storage = S3Storage()
        self.processor = DocumentProcessor()
        self.index = DocumentIndex(index_id)
        
    def upload_file(
        self, 
        file_obj: Union[BinaryIO, bytes, str], 
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        index: bool = True
    ) -> Dict[str, Any]:
        """Upload a file to S3 and optionally index it.
        
        Args:
            file_obj: File-like object, bytes, or file path
            file_name: Optional name for the file
            content_type: Optional MIME type
            metadata: Optional metadata to attach to the file
            index: Whether to index the file for search
            
        Returns:
            Dict with file information
        """
        # Create a copy of the file for indexing if needed
        if index and isinstance(file_obj, (io.BytesIO, bytes)):
            # Copy the bytes for indexing
            if isinstance(file_obj, io.BytesIO):
                # Get bytes and reset the original file pointer
                file_bytes = file_obj.getvalue()
                file_obj.seek(0)
                indexing_file = io.BytesIO(file_bytes)
            else:
                file_bytes = file_obj
                indexing_file = io.BytesIO(file_bytes)
        elif index and isinstance(file_obj, str):
            # It's a file path, we'll read it for indexing after upload
            indexing_path = file_obj
            indexing_file = None
        else:
            indexing_file = None
        
        # Upload the file to S3
        file_id = self.storage.upload_file(
            file_obj=file_obj,
            file_name=file_name,
            content_type=content_type,
            metadata=metadata
        )
        
        # Index the file if requested
        if index:
            if indexing_file is None and isinstance(file_obj, str):
                # Read the file from the provided path
                with open(indexing_path, 'rb') as f:
                    indexing_file = io.BytesIO(f.read())
            
            if indexing_file is not None:
                # Process and index the document
                chunks = self.processor.process_document(
                    file_obj=indexing_file,
                    file_name=file_name,
                    mime_type=content_type
                )
                
                # Add document to index
                if chunks:
                    self.index.add_document(
                        file_id=file_id,
                        chunks=chunks,
                        metadata={
                            'file_name': file_name or "unknown",
                            'content_type': content_type or "unknown",
                            **(metadata or {})
                        }
                    )
            else:
                # If we couldn't get a file for indexing, download it from S3
                downloaded_file, _ = self.storage.download_file(file_id)
                chunks = self.processor.process_document(
                    file_obj=downloaded_file,
                    file_name=file_name,
                    mime_type=content_type
                )
                
                # Add document to index
                if chunks:
                    self.index.add_document(
                        file_id=file_id,
                        chunks=chunks,
                        metadata={
                            'file_name': file_name or "unknown",
                            'content_type': content_type or "unknown",
                            **(metadata or {})
                        }
                    )
        
        # Return file information
        return {
            'file_id': file_id,
            'file_name': file_name,
            'content_type': content_type,
            'indexed': index,
            'metadata': metadata or {}
        }
    
    def download_file(self, file_id: str) -> Tuple[io.BytesIO, Dict[str, str]]:
        """Download a file from S3.
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            Tuple containing:
                io.BytesIO: File contents
                Dict[str, str]: File metadata
        """
        return self.storage.download_file(file_id)
    
    def delete_file(self, file_id: str, remove_from_index: bool = True) -> bool:
        """Delete a file from S3 and optionally from the index.
        
        Args:
            file_id: ID of the file to delete
            remove_from_index: Whether to also remove from index
            
        Returns:
            bool: True if deletion was successful
        """
        # Delete from S3
        success = self.storage.delete_file(file_id)
        
        # Remove from index if requested
        if success and remove_from_index:
            self.index.remove_document(file_id)
            
        return success
    
    def search(
        self, 
        query: str, 
        limit: int = 5,
        file_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search indexed documents using semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            file_id: Optional file ID to restrict search to
            
        Returns:
            List of search results with content and metadata
        """
        return self.index.search(query, limit, filter_by_file_id=file_id)
    
    def list_files(self, prefix: Optional[str] = None, max_files: int = 100) -> List[Dict[str, Any]]:
        """List files stored in S3.
        
        Args:
            prefix: Optional prefix to filter files
            max_files: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        files = self.storage.list_files(prefix, max_files)
        
        # Enrich with index metadata if available
        for file in files:
            file_id = file['id']
            index_metadata = self.index.get_document_metadata(file_id)
            if index_metadata:
                file['indexed'] = True
                file['index_metadata'] = index_metadata
            else:
                file['indexed'] = False
                
        return files
    
    def update_metadata(self, file_id: str, metadata: Dict[str, str]) -> bool:
        """Update metadata for a file in S3 and the index.
        
        Args:
            file_id: ID of the file
            metadata: New metadata to merge with existing
            
        Returns:
            bool: True if update was successful
        """
        # Update in S3
        s3_success = self.storage.update_file_metadata(file_id, metadata)
        
        # Update in index if the file is indexed
        index_metadata = self.index.get_document_metadata(file_id)
        if index_metadata:
            # Get existing chunks
            file_content, _ = self.storage.download_file(file_id)
            
            # Re-process the document
            chunks = self.processor.process_document(
                file_obj=file_content,
                file_name=metadata.get('file_name') or index_metadata.get('metadata', {}).get('file_name'),
                mime_type=metadata.get('content_type') or index_metadata.get('metadata', {}).get('content_type')
            )
            
            # Remove old document from index
            self.index.remove_document(file_id)
            
            # Add updated document to index
            if chunks:
                self.index.add_document(
                    file_id=file_id,
                    chunks=chunks,
                    metadata={
                        **(index_metadata.get('metadata', {})),
                        **metadata
                    }
                )
                
        return s3_success 