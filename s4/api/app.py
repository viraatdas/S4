"""Main FastAPI application for S4."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from s4 import config
from s4.api.routes import router as s4_router
from s4.api.admin import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="S4 - Smart S3 Storage Service",
    description="A smart storage service that combines S3 with semantic search capabilities",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
)

# Include routers
app.include_router(s4_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "S4 - Smart S3 Storage Service",
        "version": "0.1.0",
        "status": "online",
        "mode": "multi-tenant" if not config.DISABLE_API_AUTH else "single-tenant"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"} 