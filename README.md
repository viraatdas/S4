# S4 - Smart S3 Storage Service

S4 is an intelligent wrapper around Amazon S3 that leverages large language models (LLMs) to automatically index and retrieve files. When files are uploaded to S3 through the S4 service, they are automatically processed, indexed, and made available for semantic search and retrieval.

## Features

- Seamless S3 integration for file storage
- Automatic document indexing with LLMs
- Semantic search capabilities
- RESTful API for file operations
- Intelligent file retrieval based on natural language queries
- Command-line interface for common operations

## Requirements

- Python 3.8 or higher
- AWS account with S3 access
- OpenAI API key

## Setup

1. Clone this repository
   ```
   git clone https://github.com/yourusername/S4.git
   cd S4
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables
   
   Copy the example environment file:
   ```
   cp .env.example .env
   ```
   
   Edit the `.env` file with your AWS and OpenAI credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_aws_region
   S3_BUCKET_NAME=your_bucket_name
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the service
   ```
   python -m s4
   ```

## API Usage

Once the server is running, you can access the API documentation at:

```
http://localhost:8000/docs
```

### Key Endpoints:

- `POST /files/`: Upload a file
- `GET /files/`: List files
- `GET /files/{file_id}`: Download a file
- `DELETE /files/{file_id}`: Delete a file
- `POST /search/`: Semantic search
- `PUT /files/{file_id}/metadata`: Update file metadata

## CLI Usage

S4 also provides a command-line interface for common operations:

### Upload a file
```
python -m s4.cli upload path/to/file.pdf --metadata '{"category": "documentation"}'
```

### List files
```
python -m s4.cli list --limit 10
```

### Download a file
```
python -m s4.cli download file_id --output downloaded_file.pdf
```

### Delete a file
```
python -m s4.cli delete file_id
```

### Search for files
```
python -m s4.cli search "query about the document content"
```

## Supported File Types

S4 can process and index the following file types:

- Text files (.txt, .md, etc.)
- PDF documents (.pdf)
- Word documents (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- JSON files (.json)
- YAML files (.yaml, .yml)

For other file types, S4 will attempt to extract text content if possible, or store them without indexing.

## Development

### Project Structure

```
S4/
├── s4/
│   ├── api/             # FastAPI application
│   ├── indexer/         # Document indexing
│   ├── service/         # Main service logic
│   ├── storage/         # S3 storage interface
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py           # Command-line interface
│   └── config.py        # Configuration
├── data/                # Local storage for indices
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

### Adding Support for New File Types

To add support for new file types, extend the `_extract_text` method in `s4/indexer/document_processor.py`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
