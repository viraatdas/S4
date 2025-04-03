"""Unified logging configuration for S4."""

import logging
import os
import sys
from typing import Optional

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Get log level from environment variable
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


def configure_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
):
    """Configure logging for the application.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format string
        log_file: Path to log file (if None, logs to stderr)
    """
    # Use provided values or defaults
    log_level = log_level or LOG_LEVEL
    log_format = log_format or DEFAULT_LOG_FORMAT
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Configure file handler if log file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Always add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Log configuration details
    logging.info(f"Logging configured with level: {log_level}")
    if log_file:
        logging.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
