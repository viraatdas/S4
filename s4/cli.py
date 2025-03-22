"""Command-line interface for S4."""

import argparse
import json
import logging
import os
import sys
from typing import Optional, Dict, Any

from s4 import __version__
from s4 import config
from s4.service import S4Service

logger = logging.getLogger(__name__)

def setup_logging(debug: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def upload_file(args):
    """Upload a file to S3."""
    service = S4Service()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        return 1
        
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("Error: Invalid JSON metadata")
            return 1
    
    # Upload the file
    try:
        file_info = service.upload_file(
            file_obj=args.file,
            file_name=os.path.basename(args.file),
            metadata=metadata,
            index=not args.no_index
        )
        print(json.dumps(file_info, indent=2))
        print(f"\nFile uploaded successfully with ID: {file_info['file_id']}")
        return 0
    except Exception as e:
        print(f"Error uploading file: {e}")
        return 1

def list_files(args):
    """List files in S3 bucket."""
    service = S4Service()
    
    try:
        files = service.list_files(prefix=args.prefix, max_files=args.limit)
        if not files:
            print("No files found.")
            return 0
            
        # Print file information
        print(f"Found {len(files)} files:")
        for file in files:
            print(f"\nID: {file['id']}")
            print(f"Size: {file['size']} bytes")
            print(f"Last Modified: {file['last_modified']}")
            print(f"Indexed: {file['indexed']}")
            if file['metadata']:
                print("Metadata:")
                for key, value in file['metadata'].items():
                    print(f"  {key}: {value}")
        return 0
    except Exception as e:
        print(f"Error listing files: {e}")
        return 1

def download_file(args):
    """Download a file from S3."""
    service = S4Service()
    
    try:
        file_content, metadata = service.download_file(args.file_id)
        
        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            # Try to get original filename from metadata or use file_id
            if 'filename' in metadata:
                output_file = metadata['filename']
            elif '/' in args.file_id:
                output_file = args.file_id.split('/')[-1]
            else:
                output_file = args.file_id
                
        # Write file to disk
        with open(output_file, 'wb') as f:
            f.write(file_content.getvalue())
            
        print(f"File downloaded successfully to: {output_file}")
        return 0
    except FileNotFoundError:
        print(f"Error: File not found: {args.file_id}")
        return 1
    except Exception as e:
        print(f"Error downloading file: {e}")
        return 1

def delete_file(args):
    """Delete a file from S3."""
    service = S4Service()
    
    try:
        success = service.delete_file(args.file_id, remove_from_index=not args.keep_index)
        if success:
            print(f"File {args.file_id} deleted successfully")
            return 0
        else:
            print(f"Failed to delete file {args.file_id}")
            return 1
    except FileNotFoundError:
        print(f"Error: File not found: {args.file_id}")
        return 1
    except Exception as e:
        print(f"Error deleting file: {e}")
        return 1

def search(args):
    """Search files using semantic search."""
    service = S4Service()
    
    try:
        results = service.search(
            query=args.query,
            limit=args.limit,
            file_id=args.file_id
        )
        
        if not results:
            print("No results found.")
            return 0
            
        print(f"Found {len(results)} results for query: \"{args.query}\"")
        
        for i, result in enumerate(results):
            print(f"\n[{i+1}] Score: {result['score']:.4f}")
            print(f"Content: {result['content'][:200]}..." if len(result['content']) > 200 else f"Content: {result['content']}")
            print(f"File: {result['metadata'].get('file_id', 'unknown')}")
            if 'file_name' in result['metadata']:
                print(f"Filename: {result['metadata']['file_name']}")
                
        return 0
    except Exception as e:
        print(f"Error searching: {e}")
        return 1

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="S4 Command Line Interface")
    parser.add_argument('--version', action='version', version=f'S4 {__version__}')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file to S3')
    upload_parser.add_argument('file', help='Path to the file to upload')
    upload_parser.add_argument('--metadata', help='JSON metadata to attach to the file')
    upload_parser.add_argument('--no-index', action='store_true', help='Do not index the file')
    upload_parser.set_defaults(func=upload_file)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files in S3')
    list_parser.add_argument('--prefix', help='Filter files by prefix')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of files to list')
    list_parser.set_defaults(func=list_files)
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file from S3')
    download_parser.add_argument('file_id', help='ID of the file to download')
    download_parser.add_argument('--output', '-o', help='Output file path')
    download_parser.set_defaults(func=download_file)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a file from S3')
    delete_parser.add_argument('file_id', help='ID of the file to delete')
    delete_parser.add_argument('--keep-index', action='store_true', help='Keep the file in the search index')
    delete_parser.set_defaults(func=delete_file)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search files using semantic search')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=5, help='Maximum number of results')
    search_parser.add_argument('--file-id', help='Restrict search to a specific file')
    search_parser.set_defaults(func=search)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    
    # Validate configuration
    try:
        config.validate_config()
    except EnvironmentError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Run the specified command
    if not args.command:
        parser.print_help()
        return 0
        
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main()) 