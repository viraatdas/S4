# S4 Architecture

This document provides an overview of the S4 (Smart S3 Storage Service) architecture and codebase organization.

## System Overview

S4 is a service that combines S3 storage with intelligent document indexing and search capabilities. The system consists of:

1. **Backend API**: A FastAPI-based service that provides RESTful endpoints for file operations
2. **Frontend UI**: A React-based web interface for user interaction
3. **Storage Layer**: Integration with S3 for file storage
4. **Indexing Engine**: Vector-based document indexing for semantic search
5. **Authentication**: User authentication via SuperTokens and API keys

## Directory Structure

```
S4/
├── s4/                     # Core backend Python package
│   ├── api/                # FastAPI routes and API definitions
│   ├── auth/               # Authentication modules
│   ├── db/                 # Database models and operations
│   ├── indexer/            # Document indexing and search
│   ├── models/             # Data models
│   ├── service/            # Core service logic
│   ├── storage/            # Storage abstraction (S3)
│   └── utils/              # Utility functions
├── s4-ui/                  # Frontend React application
│   ├── public/             # Static assets
│   └── src/                # React source code
│       ├── components/     # Reusable UI components
│       ├── config/         # Configuration files
│       ├── pages/          # Page components
│       ├── services/       # API service clients
│       └── styles/         # CSS and styling
├── docs/                   # Documentation
├── tests/                  # Test suite
└── uploaded_docs/          # Local storage for development
```

## Key Components

### Backend Components

#### S4Service (`s4/service.py`)

The main service class that orchestrates storage and indexing operations. It provides methods for:
- Uploading files
- Downloading files
- Searching files
- Managing file metadata
- Tracking tenant usage

#### Storage (`s4/storage/s3.py`)

Handles interaction with S3 storage, including:
- File upload/download
- Metadata management
- Storage operations

#### Indexer (`s4/indexer/`)

Responsible for document processing and indexing:
- Document text extraction
- Vector embedding generation
- Semantic search

#### API (`s4/api/`)

FastAPI routes and endpoints:
- File operations (upload, download, delete)
- Search functionality
- Authentication

### Frontend Components

#### Authentication (`s4-ui/src/config/supertokens.js`)

Handles user authentication using SuperTokens:
- Google OAuth integration
- Session management

#### Pages (`s4-ui/src/pages/`)

Main application pages:
- Dashboard
- Document management
- Search interface
- User profile

#### Services (`s4-ui/src/services/`)

API client services:
- File operations
- Authentication
- Search

## Authentication Flow

1. Users authenticate via Google OAuth through SuperTokens
2. The frontend receives and stores authentication tokens
3. API requests include authentication headers
4. The backend validates tokens and associates users with tenants

## Multi-tenancy

S4 supports multi-tenant operation:
- Each tenant has isolated storage and indexing
- Usage tracking per tenant
- Plan-based limits (storage, API requests)

## Deployment Options

Multiple deployment options are supported:
- Docker containers
- AWS Amplify (frontend)
- AWS Elastic Beanstalk
- AWS ECS

See `DEPLOYMENT.md` for detailed deployment instructions.

## Environment Configuration

Environment variables control the application configuration:
- S3 bucket and region
- Authentication credentials
- API settings
- Database connection

See `env-unified-template.txt` for all available configuration options.

## Development Workflow

1. Set up environment variables using the template
2. Run the backend with `python -m s4`
3. Run the frontend with `cd s4-ui && npm start`
4. Use the unified deployment script for production deployment
