"""Main entry point for S4 service."""

import logging
import sys
import uvicorn
import click

from s4 import config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """S4 - Smart S3 Storage Service."""
    pass

@cli.command()
@click.option(
    "--host", 
    default=config.API_HOST, 
    help="Host to bind the API server to"
)
@click.option(
    "--port", 
    default=config.API_PORT, 
    type=int, 
    help="Port to bind the API server to"
)
@click.option(
    "--reload", 
    is_flag=True, 
    default=config.DEBUG, 
    help="Enable auto-reload for development"
)
def start(host, port, reload):
    """Start the S4 API server."""
    # Validate configuration
    if not config.validate_config():
        logger.error("Invalid configuration. Please check your settings.")
        sys.exit(1)
        
    # Log service mode
    if config.DISABLE_API_AUTH:
        logger.info("Starting S4 in SINGLE-TENANT mode")
    else:
        logger.info("Starting S4 in MULTI-TENANT mode")
        
    logger.info(f"Starting S4 API server on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        "s4.api.app:app",
        host=host,
        port=port,
        reload=reload
    )

@cli.command()
def init():
    """Initialize the S4 service."""
    # Create directories
    config.create_directories()
    
    # Validate configuration
    if not config.validate_config():
        logger.error("Invalid configuration. Please check your settings.")
        sys.exit(1)
        
    logger.info("S4 service initialized successfully")
    logger.info(f"Data directory: {config.DATA_DIR}")
    logger.info(f"Index storage: {config.INDEX_STORAGE_PATH}")
    logger.info(f"Tenant storage: {config.TENANT_STORAGE_PATH}")
    
    # Create initial tenant if in multi-tenant mode and confirm admin key
    if not config.DISABLE_API_AUTH:
        logger.info("Multi-tenant mode enabled")
        logger.info(f"Admin API key: {config.ADMIN_API_KEY}")
        if config.ADMIN_API_KEY == "s4-admin-dev-key":
            logger.warning("Using default admin API key! Change this in production.")

@cli.command()
def version():
    """Show S4 version information."""
    import pkg_resources
    try:
        version = pkg_resources.get_distribution("s4-storage").version
    except pkg_resources.DistributionNotFound:
        version = "development"
    
    click.echo(f"S4 - Smart S3 Storage Service")
    click.echo(f"Version: {version}")

if __name__ == "__main__":
    cli() 