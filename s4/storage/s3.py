"""AWS S3 storage interface for S4."""

import io
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, BinaryIO, Tuple

import boto3
from botocore.exceptions import ClientError

from s4 import config
from s4.exceptions import StorageError, FileNotFoundError
from s4.embedding.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class S3Storage:
    """Interface for S3 storage operations."""
    
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: Optional[str] = None,
        bucket_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        document_processor: Optional[DocumentProcessor] = None
    ):
        """Initialize S3 client with AWS credentials.
        
        Args:
            aws_access_key_id: Optional AWS access key ID
            aws_secret_access_key: Optional AWS secret access key
            aws_region: Optional AWS region
            bucket_name: Optional S3 bucket name
            tenant_id: Optional tenant ID for multi-tenant mode
            document_processor: Optional document processor for text extraction and embeddings
        """
        # Use provided credentials or fall back to config
        self.aws_access_key_id = aws_access_key_id or config.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = aws_secret_access_key or config.AWS_SECRET_ACCESS_KEY
        self.aws_region = aws_region or config.AWS_REGION
        self.bucket_name = bucket_name or config.S3_BUCKET_NAME
        self.tenant_id = tenant_id
        
        self.document_processor = document_processor or DocumentProcessor()
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region,
        )
        
        self._ensure_bucket_exists()
        
    def _ensure_bucket_exists(self):
        """Ensure the configured S3 bucket exists."""
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists and is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Bucket {self.bucket_name} not found, creating...")
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.aws_region
                    } if self.aws_region != 'us-east-1' else {}
                )
                logger.info(f"Created bucket {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {e}")
                raise StorageError(f"Error accessing bucket: {str(e)}")
    
    def _get_object_key(self, file_id: str) -> str:
        """Get the full S3 object key for a file ID.
        
        In multi-tenant mode, this prefixes the key with the tenant ID.
        
        Args:
            file_id: The file ID
            
        Returns:
            str: The S3 object key
        """
        if self.tenant_id:
            return f"{self.tenant_id}/{file_id}"
        return file_id
        
    def _get_file_id(self, object_key: str) -> str:
        """Get the file ID from an S3 object key.
        
        In multi-tenant mode, this removes the tenant ID prefix.
        
        Args:
            object_key: The S3 object key
            
        Returns:
            str: The file ID
        """
        if self.tenant_id and object_key.startswith(f"{self.tenant_id}/"):
            return object_key[len(f"{self.tenant_id}/"):]
        return object_key
    
    def upload_file(
        self, 
        file_obj: Union[BinaryIO, bytes, str], 
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        generate_embedding: bool = True
    ) -> str:
        """Upload a file to S3.
        
        Args:
            file_obj: File-like object, bytes, or path to file
            file_name: Optional name for the file (will be used in S3 key)
            content_type: Optional MIME type
            metadata: Optional metadata dictionary
            generate_embedding: Whether to generate embeddings for the file
            
        Returns:
            str: The file ID (not the full S3 key)
        """
        if isinstance(file_obj, str):
            # Assume it's a file path
            with open(file_obj, 'rb') as f:
                return self.upload_file(f, file_name or file_obj.split('/')[-1], content_type, metadata, generate_embedding)
        
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Use provided filename or generate one
        if file_name:
            # Ensure filename is safe
            safe_name = file_name.replace(' ', '_').lower()
            file_id = f"{file_id}/{safe_name}"
        
        # Get full S3 key (may include tenant prefix)
        key = self._get_object_key(file_id)
            
        # Prepare the upload parameters
        upload_args = {
            'Bucket': self.bucket_name,
            'Key': key,
        }
        
        # Add content type if provided
        if content_type:
            upload_args['ContentType'] = content_type
            
        # Add metadata if provided
        if metadata:
            # S3 metadata keys must be prefixed with 'x-amz-meta-'
            # and values must be strings
            s3_metadata = {k: str(v) for k, v in metadata.items()}
            upload_args['Metadata'] = s3_metadata
            
        # Add timestamp metadata
        timestamp = datetime.utcnow().isoformat()
        if 'Metadata' not in upload_args:
            upload_args['Metadata'] = {}
        upload_args['Metadata']['uploaded-at'] = timestamp
        
        if generate_embedding:
            if isinstance(file_obj, bytes):
                file_content_copy = io.BytesIO(file_obj)
                upload_args['Body'] = io.BytesIO(file_obj)
            else:
                current_pos = file_obj.tell()
                file_obj.seek(0)
                content = file_obj.read()
                file_content_copy = io.BytesIO(content)
                upload_args['Body'] = io.BytesIO(content)
                file_obj.seek(current_pos)
        else:
            if isinstance(file_obj, bytes):
                upload_args['Body'] = io.BytesIO(file_obj)
            else:
                # Assume it's a file-like object
                upload_args['Body'] = file_obj
            
        try:
            self.s3.upload_fileobj(**upload_args)
            logger.info(f"Uploaded file to S3: {key}")
            
            if generate_embedding:
                try:
                    doc_info = self.document_processor.process_document(
                        file_content_copy, 
                        file_name or "unknown", 
                        content_type
                    )
                    
                    embedding_metadata = {
                        "indexed": "true",
                        "embedding_model": config.EMBEDDING_MODEL,
                        "tokens": str(doc_info.get("tokens", 0)),
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                    
                    self.update_file_metadata(file_id, embedding_metadata)
                    
                    logger.info(f"Generated embeddings for file: {key}")
                except Exception as e:
                    logger.error(f"Error generating embeddings for file {key}: {e}")
                    self.update_file_metadata(file_id, {"indexed": "false", "indexing_error": str(e)})
            
            return file_id
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise StorageError(f"Error uploading file: {str(e)}")
    
    def download_file(self, file_id: str) -> Tuple[io.BytesIO, Dict[str, str]]:
        """Download a file from S3.
        
        Args:
            file_id: The file ID (not the full S3 key)
            
        Returns:
            Tuple containing:
                io.BytesIO: File contents as bytes
                Dict[str, str]: File metadata
        """
        # Get full S3 key (may include tenant prefix)
        key = self._get_object_key(file_id)
        
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            file_content = io.BytesIO(response['Body'].read())
            metadata = response.get('Metadata', {})
            return file_content, metadata
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"File not found: {key}")
                raise FileNotFoundError(file_id)
            logger.error(f"Error downloading file from S3: {e}")
            raise StorageError(f"Error downloading file: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from S3.
        
        Args:
            file_id: The file ID (not the full S3 key)
            
        Returns:
            bool: True if deletion was successful
        """
        # Get full S3 key (may include tenant prefix)
        key = self._get_object_key(file_id)
        
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted file from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise StorageError(f"Error deleting file: {str(e)}")
    
    def list_files(self, prefix: Optional[str] = None, max_keys: int = 1000) -> List[Dict]:
        """List files in the S3 bucket.
        
        Args:
            prefix: Optional prefix to filter keys
            max_keys: Maximum number of keys to return
            
        Returns:
            List[Dict]: List of file information dictionaries
        """
        try:
            # In multi-tenant mode, always prefix with tenant ID
            full_prefix = None
            if self.tenant_id:
                full_prefix = f"{self.tenant_id}/"
                if prefix:
                    full_prefix += prefix
            else:
                full_prefix = prefix
                
            params = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_keys,
            }
            
            if full_prefix:
                params['Prefix'] = full_prefix
                
            response = self.s3.list_objects_v2(**params)
            
            if 'Contents' not in response:
                return []
                
            files = []
            for item in response['Contents']:
                # Get metadata for each object
                try:
                    obj = self.s3.head_object(Bucket=self.bucket_name, Key=item['Key'])
                    
                    # Remove tenant prefix from keys for client response
                    file_id = self._get_file_id(item['Key'])
                    
                    files.append({
                        'id': file_id,
                        'size': item['Size'],
                        'last_modified': item['LastModified'].isoformat(),
                        'metadata': obj.get('Metadata', {})
                    })
                except ClientError:
                    # If there's an error getting metadata, just use the basic info
                    # Remove tenant prefix from keys for client response
                    file_id = self._get_file_id(item['Key'])
                    
                    files.append({
                        'id': file_id,
                        'size': item['Size'],
                        'last_modified': item['LastModified'].isoformat(),
                        'metadata': {}
                    })
                    
            return files
        except ClientError as e:
            logger.error(f"Error listing files from S3: {e}")
            raise StorageError(f"Error listing files: {str(e)}")
            
    def get_file_metadata(self, file_id: str) -> Dict[str, str]:
        """Get metadata for a file.
        
        Args:
            file_id: The file ID (not the full S3 key)
            
        Returns:
            Dict[str, str]: File metadata
        """
        # Get full S3 key (may include tenant prefix)
        key = self._get_object_key(file_id)
        
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return response.get('Metadata', {})
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey' or e.response['Error']['Code'] == '404':
                logger.error(f"File not found: {key}")
                raise FileNotFoundError(file_id)
            logger.error(f"Error getting file metadata from S3: {e}")
            raise StorageError(f"Error getting file metadata: {str(e)}")
            
    def update_file_metadata(self, file_id: str, metadata: Dict[str, str]) -> bool:
        """Update metadata for a file.
        
        Args:
            file_id: The file ID (not the full S3 key)
            metadata: New metadata dictionary
            
        Returns:
            bool: True if update was successful
        """
        # Get full S3 key (may include tenant prefix)
        key = self._get_object_key(file_id)
        
        try:
            # Get existing metadata
            existing_metadata = self.get_file_metadata(file_id)
            
            # Merge with new metadata
            merged_metadata = {**existing_metadata, **metadata}
            
            # Copy object to itself with new metadata
            copy_source = {'Bucket': self.bucket_name, 'Key': key}
            self.s3.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=key,
                Metadata=merged_metadata,
                MetadataDirective='REPLACE'
            )
            
            logger.info(f"Updated metadata for file: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error updating file metadata in S3: {e}")
            raise StorageError(f"Error updating file metadata: {str(e)}")  