"""Configuration for S4."""

import os
import logging
from pathlib import Path
from typing import List, Set, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Debug mode
DEBUG = os.getenv("S4_DEBUG", "False").lower() in ("true", "1", "t")

# API settings
API_HOST = os.getenv("S4_API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("S4_API_PORT", "8000"))

# Authentication settings
DISABLE_API_AUTH = os.getenv("S4_DISABLE_API_AUTH", "False").lower() in ("true", "1", "t")
DEFAULT_API_KEY = os.getenv("S4_API_KEY", "s4-dev-key")
ADMIN_API_KEY = os.getenv("S4_ADMIN_API_KEY", "s4-admin-dev-key")

# CORS settings
CORS_ORIGINS = os.getenv("S4_CORS_ORIGINS", "*").split(",")

# S3 storage settings
S3_BUCKET = os.getenv("S4_S3_BUCKET")
S3_REGION = os.getenv("S4_S3_REGION", "us-east-1")
S3_PREFIX = os.getenv("S4_S3_PREFIX", "")
S3_ENDPOINT_URL = os.getenv("S4_S3_ENDPOINT_URL")  # For non-AWS S3 (e.g., MinIO)

# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("S4_EMBEDDING_MODEL", "text-embedding-ada-002")
MAX_CHUNK_SIZE = int(os.getenv("S4_MAX_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("S4_CHUNK_OVERLAP", "200"))

# Local storage paths
APP_DIR = Path(__file__).parent
DATA_DIR = Path(os.getenv("S4_DATA_DIR", Path.home() / ".s4"))
TEMP_DIR = DATA_DIR / "temp"
INDEX_STORAGE_PATH = DATA_DIR / "indices"
TENANT_STORAGE_PATH = DATA_DIR / "tenants"

# Multi-tenant settings
DEFAULT_PLAN_ID = os.getenv("S4_DEFAULT_PLAN_ID", "basic")
TENANT_ISOLATION_MODE = os.getenv("S4_TENANT_ISOLATION_MODE", "prefix")  # 'bucket', 'prefix'

# Create necessary directories
def create_directories():
    """Create necessary directories for S4."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(INDEX_STORAGE_PATH, exist_ok=True)
    os.makedirs(TENANT_STORAGE_PATH, exist_ok=True)
    
create_directories()

# Configuration validation
def validate_config():
    """Validate the configuration."""
    errors = []
    
    # In single-tenant mode, check S3 settings
    if DISABLE_API_AUTH:
        if not S3_BUCKET:
            errors.append("S4_S3_BUCKET must be set in single-tenant mode")
            
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            errors.append("AWS credentials must be set in single-tenant mode")
            
    # Check OpenAI API key
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY must be set")
        
    # In multi-tenant mode, check admin API key
    if not DISABLE_API_AUTH and ADMIN_API_KEY == "s4-admin-dev-key":
        logger.warning("Using default admin API key in production is not recommended")
        
    if errors:
        for error in errors:
            logger.error(error)
        return False
    
    return True 