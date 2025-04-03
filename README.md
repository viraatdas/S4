# S4: Semantic Search Service

S4 is a fully-featured semantic search service with multi-tenant support, designed to help organizations integrate powerful semantic search capabilities into their applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

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

### Using Docker Compose (Local Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/s4.git
   cd s4
   ```

2. Run the deployment script:
   ```bash
   ./deploy_docker.sh
   ```

3. Follow the prompts to configure your environment. You'll need:
   - OpenAI API key
   - AWS credentials (optional for local development)
   - S3 bucket details (optional for local development)

4. Access the application:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost
   - Admin Portal: http://localhost/admin/login

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

- **Docker Compose**: For local development and testing
- **AWS Elastic Beanstalk**: For production deployment
- **AWS ECS/Fargate**: For scalable production deployment
- **AWS Amplify**: For frontend-only deployment

See the [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

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

S4 can be configured using environment variables. See the [Deployment Guide](docs/DEPLOYMENT.md) for a complete list of configuration options.

## Development

### Backend Development

The backend is built with Python FastAPI:

```bash
cd s4
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
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
