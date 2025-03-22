"""Main entry point for S4."""

import argparse
import logging
import sys

from s4 import __version__
from s4.api.app import run_server
from s4 import config

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the S4 application."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="S4 - Smart S3 Storage Service")
    parser.add_argument('--version', action='version', version=f'S4 {__version__}')
    parser.add_argument('--host', help=f'API host (default: {config.API_HOST})')
    parser.add_argument('--port', type=int, help=f'API port (default: {config.API_PORT})')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.host:
        config.API_HOST = args.host
    if args.port:
        config.API_PORT = args.port
    if args.debug:
        config.DEBUG = True
    
    # Set up logging
    logging_level = logging.DEBUG if config.DEBUG else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Validate configuration
    try:
        config.validate_config()
    except EnvironmentError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the server
    logger.info(f"Starting S4 server v{__version__}")
    run_server()

if __name__ == "__main__":
    main() 