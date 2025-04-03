"""Unified error handling for S4."""

import logging
import traceback
from typing import Dict, Any, Optional, Type, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from s4.exceptions import S4Error, ValidationError, StorageError, IndexError

# Get logger
logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions in a consistent way."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle any exceptions.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            Response object
        """
        try:
            return await call_next(request)
        except Exception as exc:
            # Log the exception
            logger.error(f"Unhandled exception: {str(exc)}")
            logger.debug(traceback.format_exc())
            
            # Map exception to appropriate status code and message
            status_code, error_detail = map_exception_to_response(exc)
            
            # Return JSON response with error details
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": error_detail,
                    "status_code": status_code,
                    "path": request.url.path
                }
            )


def map_exception_to_response(exc: Exception) -> tuple[int, str]:
    """Map an exception to an appropriate HTTP status code and error message.
    
    Args:
        exc: The exception to map
        
    Returns:
        Tuple of (status_code, error_detail)
    """
    # Define mapping of exception types to status codes
    exception_map: Dict[Type[Exception], int] = {
        ValidationError: 400,
        StorageError: 404,
        IndexError: 500,
        S4Error: 500,
        ValueError: 400,
        KeyError: 404,
        NotImplementedError: 501,
    }
    
    # Get status code based on exception type
    for exc_type, status_code in exception_map.items():
        if isinstance(exc, exc_type):
            return status_code, str(exc)
    
    # Default to 500 for unhandled exceptions
    return 500, "Internal server error"


def format_error_response(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format a consistent error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        details: Additional error details
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "error": message,
        "status_code": status_code
    }
    
    if details:
        response["details"] = details
        
    return response
