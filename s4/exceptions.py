"""Custom exceptions for S4."""

class S4Error(Exception):
    """Base exception for all S4-related errors."""
    
    def __init__(self, message: str = "An error occurred in S4"):
        self.message = message
        super().__init__(self.message)

class ConfigError(S4Error):
    """Error related to configuration."""
    
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message)

class StorageError(S4Error):
    """Error related to S3 storage operations."""
    
    def __init__(self, message: str = "Storage error"):
        super().__init__(message)

class FileNotFoundError(S4Error):
    """Error when a file is not found."""
    
    def __init__(self, file_id: str):
        message = f"File not found: {file_id}"
        super().__init__(message)

class IndexError(S4Error):
    """Error related to document indexing."""
    
    def __init__(self, message: str = "Indexing error"):
        super().__init__(message)

class ProcessingError(S4Error):
    """Error related to document processing."""
    
    def __init__(self, message: str = "Document processing error"):
        super().__init__(message)

class AuthenticationError(S4Error):
    """Error related to authentication."""
    
    def __init__(self, message: str = "Authentication error"):
        super().__init__(message)

class ValidationError(S4Error):
    """Exception for validation errors."""
    pass

class TenantError(S4Error):
    """Exception for tenant management errors."""
    pass

class LimitExceededError(ValidationError):
    """Exception for when a tenant exceeds their plan limits."""
    pass 