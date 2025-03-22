"""AWS S3 storage interface for S4."""

import io
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, BinaryIO, Tuple

import boto3
from botocore.exceptions import ClientError

from s4 import config

logger = logging.getLogger(__name__)

class S3Storage:
    """Interface for S3 storage operations."""
    
    def __init__(self):
        """Initialize S3 client with AWS credentials."""
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
        )
        self.bucket_name = config.S3_BUCKET_NAME
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
                        'LocationConstraint': config.AWS_REGION
                    } if config.AWS_REGION != 'us-east-1' else {}
                )
                logger.info(f"Created bucket {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
    
    def upload_file(
        self, 
        file_obj: Union[BinaryIO, bytes, str], 
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload a file to S3.
        
        Args:
            file_obj: File-like object, bytes, or path to file
            file_name: Optional name for the file (will be used in S3 key)
            content_type: Optional MIME type
            metadata: Optional metadata dictionary
            
        Returns:
            str: The S3 key (ID) of the uploaded file
        """
        if isinstance(file_obj, str):
            # Assume it's a file path
            with open(file_obj, 'rb') as f:
                return self.upload_file(f, file_name or file_obj.split('/')[-1], content_type, metadata)
        
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Use provided filename or generate one
        if file_name:
            # Ensure filename is safe
            safe_name = file_name.replace(' ', '_').lower()
            key = f"{file_id}/{safe_name}"
        else:
            # Use only the UUID if no filename provided
            key = file_id
            
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
            
        # Handle different types of file objects
        if isinstance(file_obj, bytes):
            upload_args['Body'] = io.BytesIO(file_obj)
        else:
            # Assume it's a file-like object
            upload_args['Body'] = file_obj
            
        try:
            self.s3.upload_fileobj(**upload_args)
            logger.info(f"Uploaded file to S3: {key}")
            return key
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise
    
    def download_file(self, file_id: str) -> Tuple[io.BytesIO, Dict[str, str]]:
        """Download a file from S3.
        
        Args:
            file_id: The S3 key or ID of the file
            
        Returns:
            Tuple containing:
                io.BytesIO: File contents as bytes
                Dict[str, str]: File metadata
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_id)
            file_content = io.BytesIO(response['Body'].read())
            metadata = response.get('Metadata', {})
            return file_content, metadata
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"File not found: {file_id}")
                raise FileNotFoundError(f"File with ID {file_id} not found")
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from S3.
        
        Args:
            file_id: The S3 key or ID of the file
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_id)
            logger.info(f"Deleted file from S3: {file_id}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise
    
    def list_files(self, prefix: Optional[str] = None, max_keys: int = 1000) -> List[Dict]:
        """List files in the S3 bucket.
        
        Args:
            prefix: Optional prefix to filter keys
            max_keys: Maximum number of keys to return
            
        Returns:
            List[Dict]: List of file information dictionaries
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_keys,
            }
            
            if prefix:
                params['Prefix'] = prefix
                
            response = self.s3.list_objects_v2(**params)
            
            if 'Contents' not in response:
                return []
                
            files = []
            for item in response['Contents']:
                # Get metadata for each object
                try:
                    obj = self.s3.head_object(Bucket=self.bucket_name, Key=item['Key'])
                    files.append({
                        'id': item['Key'],
                        'size': item['Size'],
                        'last_modified': item['LastModified'].isoformat(),
                        'metadata': obj.get('Metadata', {})
                    })
                except ClientError:
                    # If there's an error getting metadata, just use the basic info
                    files.append({
                        'id': item['Key'],
                        'size': item['Size'],
                        'last_modified': item['LastModified'].isoformat(),
                        'metadata': {}
                    })
                    
            return files
        except ClientError as e:
            logger.error(f"Error listing files from S3: {e}")
            raise
            
    def get_file_metadata(self, file_id: str) -> Dict[str, str]:
        """Get metadata for a file.
        
        Args:
            file_id: The S3 key or ID of the file
            
        Returns:
            Dict[str, str]: File metadata
        """
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=file_id)
            return response.get('Metadata', {})
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey' or e.response['Error']['Code'] == '404':
                logger.error(f"File not found: {file_id}")
                raise FileNotFoundError(f"File with ID {file_id} not found")
            logger.error(f"Error getting file metadata from S3: {e}")
            raise
            
    def update_file_metadata(self, file_id: str, metadata: Dict[str, str]) -> bool:
        """Update metadata for a file.
        
        Args:
            file_id: The S3 key or ID of the file
            metadata: New metadata dictionary
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Get existing metadata
            existing_metadata = self.get_file_metadata(file_id)
            
            # Merge with new metadata
            merged_metadata = {**existing_metadata, **metadata}
            
            # Copy object to itself with new metadata
            copy_source = {'Bucket': self.bucket_name, 'Key': file_id}
            self.s3.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=file_id,
                Metadata=merged_metadata,
                MetadataDirective='REPLACE'
            )
            
            logger.info(f"Updated metadata for file: {file_id}")
            return True
        except ClientError as e:
            logger.error(f"Error updating file metadata in S3: {e}")
            raise 