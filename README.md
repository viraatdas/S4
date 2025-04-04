# S4: S3 but like WAYYY better with LLM support

S4 is a fully-featured semantic search service with multi-tenant support, designed to help organizations integrate powerful semantic search capabilities into their applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Frontend: AWS Amplify](https://img.shields.io/badge/Frontend-AWS%20Amplify-orange)](docs/deployment/aws.md)
[![Backend: AWS ECS](https://img.shields.io/badge/Backend-AWS%20ECS-yellow)](docs/deployment/aws.md)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)](docs/deployment/aws.md)
[![Deploy Status](https://img.shields.io/badge/Deploy-Success-brightgreen)](docs/deployment/aws.md)

## Features

- **Semantic Search**: Advanced vector-based search powered by OpenAI embeddings
- **Multi-tenant Architecture**: Securely isolate data and configurations for different clients
- **Document Management**: Upload, process, and search through various document types
- **API-First Design**: RESTful API for easy integration with any application
- **User-friendly Dashboard**: Modern React-based UI for document management
- **Admin Portal**: Comprehensive admin interface for tenant management and analytics
- **Subscription Plans**: Built-in subscription management for different usage tiers
- **Scalable Infrastructure**: Deployable on AWS with multiple hosting options

## Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/s4.git
   cd s4
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the backend server:
   ```bash
   cd server
   python server.py
   ```

4. In a separate terminal, start the frontend:
   ```bash
   cd s4-ui
   npm install  # Only needed first time
   npm start
   ```

5. Access the application:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:3000

## Architecture

S4 consists of two main components:

1. **Backend API** (Python FastAPI):
   - RESTful API for document and tenant management
   - Embedding generation and semantic search
   - Storage integration with S3
   - Multi-tenant data isolation

2. **Frontend UI** (React):
   - User dashboard for document management
   - Search interface with result visualization
   - Admin portal for system management
   - Authentication and subscription management

## Deployment Options

S4 supports multiple deployment methods:

- **AWS Amplify**: For frontend deployment
- **AWS ECS**: For backend deployment
- **AWS Elastic Beanstalk**: Alternative production deployment
- **Docker**: For containerized deployment

See the [Deployment Guide](docs/deployment/README.md) for detailed instructions.

## API Documentation

The S4 API provides endpoints for:

- Document management (upload, delete, search)
- User authentication and tenant management
- Subscription and plan management
- System administration and analytics

API documentation is available at `http://localhost:8000/docs` when running locally.

## Admin Portal

The Admin Portal provides a comprehensive interface for:

- Managing tenants and their subscription plans
- Monitoring system usage and analytics
- Managing system-wide settings
- Troubleshooting and system maintenance

Access the Admin Portal at `http://localhost/admin/login` with your admin API key.

## Configuration

S4 can be configured using environment variables. See the [Deployment Guide](docs/deployment/README.md) for a complete list of configuration options. A template for environment variables is available in the `.env.example` file.

## Development

### Backend Development

The backend is built with Python FastAPI:

```bash
cd server
pip install -r requirements.txt
python server.py
```

You can also run the server with hot reloading during development:

```bash
cd server
python -m uvicorn server:app --reload
```

### Frontend Development

The frontend is built with React:

```bash
cd s4-ui
npm install
npm start
```

## Testing

Run backend tests:

```bash
cd s4
pytest
```

Run frontend tests:

```bash
cd s4-ui
npm test
```

## Repository Structure

The S4 repository is organized as follows:

```
/
├── docs/                    # Documentation
│   ├── architecture/        # Architecture documentation
│   ├── deployment/          # Deployment guides
│   └── security/            # Security documentation
├── deployment/              # Deployment configurations
│   ├── aws/                 # AWS-specific configurations
│   ├── docker/              # Docker configurations
│   └── heroku/              # Heroku configurations
├── scripts/                 # Utility scripts
│   ├── deploy.sh            # Unified deployment script
│   └── ...                  # Other utility scripts
├── server/                  # Server implementations
│   └── simple_server.py     # Simple FastAPI server
├── s4/                      # Core Python package
│   ├── api/                 # API endpoints
│   ├── auth/                # Authentication modules
│   ├── db/                  # Database models and connections
│   ├── indexer/             # Document indexing and search
│   ├── models/              # Data models
│   ├── service/             # Service layer
│   └── storage/             # Storage interfaces
├── s4-ui/                   # Frontend React application
│   ├── public/              # Static assets
│   └── src/                 # React source code
├── tests/                   # Test suite
│   └── auth/                # Authentication tests
└── .env.example            # Environment variable template
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAI for providing the embedding models
- AWS for hosting infrastructure
- All contributors who have helped shape this project
