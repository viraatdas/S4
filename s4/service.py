"""S4 Service - S4 (Smart S3 Storage Service)."""

import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, BinaryIO, Tuple, Any, Union

from s4.storage.s3 import S3Storage
from s4.indexer.index import DocumentIndex
from s4.indexer.processor import DocumentProcessor
from s4.models import Tenant, Plan
from s4.db import tenant_manager
from s4.exceptions import S4Error, StorageError, IndexError, ValidationError

logger = logging.getLogger(__name__)

class S4Service:
    """Main S4 service that combines storage and indexing."""

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        storage_id: str = "default",
        index_id: str = "default",
        s3_bucket: Optional[str] = None,
        s3_region: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        """Initialize the S4 service.
        
        Args:
            tenant_id: Optional tenant ID for multi-tenant mode
            storage_id: Identifier for the storage backend
            index_id: Identifier for the document index
            s3_bucket: Optional S3 bucket name override
            s3_region: Optional S3 region override
            openai_api_key: Optional OpenAI API key override
        """
        self.tenant_id = tenant_id
        
        # Get tenant info if in multi-tenant mode
        self.tenant = None
        if tenant_id:
            self.tenant = tenant_manager.get_tenant(tenant_id)
            if not self.tenant:
                raise ValidationError(f"Tenant {tenant_id} not found")
            if not self.tenant.active:
                raise ValidationError(f"Tenant {tenant_id} is not active")
                
            # Use tenant-specific configurations if available
            s3_bucket = s3_bucket or self.tenant.s3_bucket
            s3_region = s3_region or self.tenant.s3_region
            openai_api_key = openai_api_key or self.tenant.openai_api_key
        
        # Initialize storage
        self.storage = S3Storage(
            storage_id=storage_id,
            tenant_id=tenant_id,
            bucket_name=s3_bucket,
            region_name=s3_region
        )
        
        # Initialize document index
        self.index = DocumentIndex(
            index_id=index_id,
            tenant_id=tenant_id,
            openai_api_key=openai_api_key
        )
        
        # Initialize document processor
        self.processor = DocumentProcessor()
        
    def _track_usage(self, file_size: Optional[int] = None, api_request: bool = True):
        """Track tenant usage if in multi-tenant mode.
        
        Args:
            file_size: Size of the file in bytes (for storage tracking)
            api_request: Whether to count this as an API request
        """
        if self.tenant and self.tenant_id:
            if file_size:
                tenant_manager.increment_tenant_usage(
                    self.tenant_id, 
                    storage_bytes=file_size,
                    api_request=api_request,
                    file_count=1
                )
            elif api_request:
                tenant_manager.increment_tenant_usage(
                    self.tenant_id,
                    api_request=api_request
                )
    
    def _check_tenant_limits(self, file_size: Optional[int] = None):
        """Check tenant limits if in multi-tenant mode.
        
        Args:
            file_size: Size of the file in bytes (for storage limit check)
            
        Raises:
            ValidationError: If tenant has exceeded their plan limits
        """
        if self.tenant and self.tenant_id:
            # Check limits based on file operation
            if file_size:
                # Check file size limit
                if not self.tenant.check_file_size_limit(file_size):
                    raise ValidationError(
                        f"File size exceeds tenant's plan limit of {self.tenant.plan.max_file_size_mb}MB"
                    )
                    
                # Check storage limit
                if not self.tenant.check_storage_limit(file_size):
                    raise ValidationError(
                        f"Storage use would exceed tenant's plan limit of {self.tenant.plan.storage_limit_gb}GB"
                    )
            
            # Check API request limit
            if not self.tenant.check_api_limit(1):
                raise ValidationError(
                    f"API request count would exceed tenant's plan limit of {self.tenant.plan.monthly_requests}"
                )
    
    def upload_file(
        self, 
        file_path: Union[str, Path],
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file to storage and index it.
        
        Args:
            file_path: Path to the file to upload
            file_id: Optional file ID (generated if not provided)
            metadata: Optional metadata
            
        Returns:
            File ID
        """
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        
        # Check tenant limits for multi-tenant mode
        self._check_tenant_limits(file_size)
            
        try:
            # Process document for indexing
            chunks = self.processor.process_file(file_path)
            
            # Upload to storage
            file_id = self.storage.upload_file(file_path, file_id, metadata)
            
            # Add to index if chunks were extracted
            if chunks:
                self.index.add_document(file_id, chunks, metadata)
                
            # Track usage for multi-tenant mode
            self._track_usage(file_size)
                
            return file_id
        except (StorageError, IndexError) as e:
            logger.error(f"Error uploading file: {e}")
            raise S4Error(f"Error uploading file: {str(e)}")
            
    def upload_file_object(
        self,
        file_obj: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file object to storage and index it.
        
        Args:
            file_obj: File-like object to upload
            filename: Name of the file
            content_type: MIME type of the file
            file_id: Optional file ID (generated if not provided)
            metadata: Optional metadata
            
        Returns:
            File ID
        """
        # Save the file object to a temporary file first
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
            # Copy file content to temp file
            file_obj.seek(0)
            temp_file.write(file_obj.read())
            file_obj.seek(0)  # Reset file pointer
            
            # Get file size for limit checking
            temp_file.seek(0, 2)  # Seek to end of file
            file_size = temp_file.tell()  # Get size
            temp_file.seek(0)  # Reset file pointer
            
        # Check tenant limits for multi-tenant mode
        self._check_tenant_limits(file_size)
            
        try:
            # Process the temp file
            chunks = self.processor.process_file(temp_path)
            
            # If no content type provided, try to guess
            if not content_type:
                import mimetypes
                content_type = mimetypes.guess_type(filename)[0]
                
            # Add content type to metadata
            if metadata is None:
                metadata = {}
            if content_type:
                metadata["content_type"] = content_type
                
            # Store original filename
            metadata["original_filename"] = filename
                
            # Upload to storage
            file_id = self.storage.upload_file(temp_path, file_id, metadata)
            
            # Add to index if chunks were extracted
            if chunks:
                self.index.add_document(file_id, chunks, metadata)
            
            # Track usage for multi-tenant mode
            self._track_usage(file_size)
                
            return file_id
        except (StorageError, IndexError) as e:
            logger.error(f"Error uploading file: {e}")
            raise S4Error(f"Error uploading file: {str(e)}")
        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)
            
    def download_file(
        self, 
        file_id: str, 
        output_path: Optional[Union[str, Path]] = None
    ) -> Union[Path, BinaryIO]:
        """Download a file from storage.
        
        Args:
            file_id: File ID to download
            output_path: Optional path to save the file
            
        Returns:
            Path to the downloaded file or file object
        """
        # Check tenant limits for multi-tenant mode (API request only)
        self._check_tenant_limits()
        
        try:
            result = self.storage.download_file(file_id, output_path)
            
            # Track API usage for multi-tenant mode
            self._track_usage()
            
            return result
        except StorageError as e:
            logger.error(f"Error downloading file: {e}")
            raise S4Error(f"Error downloading file: {str(e)}")
            
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from storage and index.
        
        Args:
            file_id: File ID to delete
            
        Returns:
            True if deleted successfully
        """
        # Check tenant limits for multi-tenant mode (API request only)
        self._check_tenant_limits()
        
        try:
            # Get file metadata (for tenant verification in multi-tenant mode)
            metadata = self.storage.get_file_metadata(file_id)
            
            # Delete from storage
            result = self.storage.delete_file(file_id)
            
            # Delete from index
            self.index.remove_document(file_id)
            
            # Track API usage for multi-tenant mode
            self._track_usage()
            
            return result
        except StorageError as e:
            logger.error(f"Error deleting file: {e}")
            raise S4Error(f"Error deleting file: {str(e)}")
            
    def list_files(
        self, 
        prefix: str = "", 
        max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """List files in storage.
        
        Args:
            prefix: Optional prefix to filter by
            max_results: Maximum number of results to return
            
        Returns:
            List of file metadata dictionaries
        """
        # Check tenant limits for multi-tenant mode (API request only)
        self._check_tenant_limits()
        
        try:
            result = self.storage.list_files(prefix, max_results)
            
            # Track API usage for multi-tenant mode
            self._track_usage()
            
            return result
        except StorageError as e:
            logger.error(f"Error listing files: {e}")
            raise S4Error(f"Error listing files: {str(e)}")
            
    def search_files(
        self, 
        query: str, 
        limit: int = 5,
        file_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for files using vector search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            file_id: Optional file ID to restrict search to
            
        Returns:
            List of search result dictionaries
        """
        # Check tenant limits for multi-tenant mode (API request only)
        self._check_tenant_limits()
        
        try:
            # Search the index
            results = self.index.search(query, limit, filter_by_file_id=file_id)
            
            # Enrich results with file metadata
            for result in results:
                file_id = result.get("metadata", {}).get("file_id")
                if file_id:
                    try:
                        file_metadata = self.storage.get_file_metadata(file_id)
                        # Add file metadata but preserve chunk-specific metadata
                        result["file_metadata"] = file_metadata
                    except StorageError as e:
                        logger.warning(f"Error getting file metadata for search result: {e}")
            
            # Track API usage for multi-tenant mode
            self._track_usage()
            
            return results
        except IndexError as e:
            logger.error(f"Error searching files: {e}")
            raise S4Error(f"Error searching files: {str(e)}")
            
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            Metadata dictionary
        """
        # Check tenant limits for multi-tenant mode (API request only)
        self._check_tenant_limits()
        
        try:
            result = self.storage.get_file_metadata(file_id)
            
            # Track API usage for multi-tenant mode
            self._track_usage()
            
            return result
        except StorageError as e:
            logger.error(f"Error getting file metadata: {e}")
            raise S4Error(f"Error getting file metadata: {str(e)}")
            
    def update_file_metadata(
        self, 
        file_id: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update metadata for a file.
        
        Args:
            file_id: File ID
            metadata: New metadata dictionary (merged with existing)
            
        Returns:
            Updated metadata dictionary
        """
        # Check tenant limits for multi-tenant mode (API request only)
        self._check_tenant_limits()
        
        try:
            result = self.storage.update_file_metadata(file_id, metadata)
            
            # Track API usage for multi-tenant mode
            self._track_usage()
            
            return result
        except StorageError as e:
            logger.error(f"Error updating file metadata: {e}")
            raise S4Error(f"Error updating file metadata: {str(e)}")
            
    def get_tenant_usage(self) -> Optional[Dict[str, Any]]:
        """Get tenant usage statistics.
        
        Returns:
            Dictionary with usage statistics or None if not in multi-tenant mode
        """
        if not self.tenant_id or not self.tenant:
            return None
            
        return {
            "storage_used_bytes": self.tenant.storage_used_bytes,
            "storage_limit_bytes": self.tenant.plan.storage_limit_gb * 1024 * 1024 * 1024,
            "storage_used_percentage": round(
                (self.tenant.storage_used_bytes / 
                (self.tenant.plan.storage_limit_gb * 1024 * 1024 * 1024)) * 100, 2
            ),
            "api_requests_count": self.tenant.api_requests_count,
            "api_requests_limit": self.tenant.plan.monthly_requests,
            "api_requests_percentage": round(
                (self.tenant.api_requests_count / self.tenant.plan.monthly_requests) * 100, 2
            ),
            "file_count": self.tenant.file_count,
            "plan": {
                "name": self.tenant.plan.name,
                "description": self.tenant.plan.description,
                "price_monthly": self.tenant.plan.price_monthly,
                "price_yearly": self.tenant.plan.price_yearly,
                "storage_limit_gb": self.tenant.plan.storage_limit_gb,
                "monthly_requests": self.tenant.plan.monthly_requests,
                "max_file_size_mb": self.tenant.plan.max_file_size_mb,
                "features": self.tenant.plan.features
            }
        } 