# S4 Frequently Asked Questions

This document addresses common questions about S4, its features, deployment, and usage.

## General Questions

### What is S4?

S4 (Semantic Search Service) is a multi-tenant SaaS application that provides powerful semantic search capabilities. It allows organizations to upload, index, and search documents using state-of-the-art semantic search technology, with proper tenant isolation and subscription plan management.

### How does semantic search differ from traditional search?

Traditional search relies on keyword matching, where documents are returned only if they contain the exact words in the query. Semantic search, on the other hand, understands the meaning and context of the query and returns relevant documents even if they don't contain the exact same words.

S4 uses OpenAI embeddings to convert text into vector representations that capture semantic meaning, allowing for more intuitive and accurate search results.

### What types of documents can S4 process?

S4 can process a variety of document formats, including:
- PDF
- Microsoft Word (.docx, .doc)
- Plain text (.txt)
- Markdown (.md)
- HTML
- CSV
- JSON
- And more

The document processing pipeline extracts text content from these formats and creates searchable embeddings.

### Is S4 open source?

Yes, S4 is open source and licensed under the MIT License. You can freely use, modify, and distribute it according to the terms of the license.

## Technical Questions

### What technologies does S4 use?

S4 is built with:
- **Backend**: Python with FastAPI
- **Frontend**: React with React Bootstrap
- **Storage**: AWS S3 for document storage
- **Embeddings**: OpenAI's embedding models
- **Vector Database**: FAISS for efficient similarity search
- **Container**: Docker for deployment

### What are the system requirements for running S4?

For development:
- 2 CPU cores
- 4GB RAM
- 10GB storage
- Docker 20.10+
- Python 3.9+
- Node.js 16+

For production (recommended):
- 4+ CPU cores
- 8GB+ RAM
- 100GB+ storage
- AWS account with S3 access
- OpenAI API key

### How does S4 handle multi-tenancy?

S4 implements multi-tenancy through:
- Isolated storage paths in S3 for each tenant
- Tenant-specific API keys for authentication
- Database partitioning to keep tenant data separate
- Usage tracking per tenant
- Subscription plans with tenant-specific limits

### How does S4 process and index documents?

The document processing pipeline follows these steps:
1. Document upload via API
2. Text extraction from the document
3. Text chunking into manageable segments
4. Embedding generation using OpenAI's API
5. Vector storage in the vector database
6. Metadata storage in the metadata database

### Can S4 integrate with other systems?

Yes, S4 provides a comprehensive REST API that can integrate with:
- Content management systems
- Document management systems
- Custom applications
- Business intelligence tools
- Workflow automation systems

## Deployment Questions

### How do I deploy S4?

S4 can be deployed in several ways:
1. **Docker Compose**: For local development and testing
2. **AWS Elastic Beanstalk**: For production deployment
3. **AWS ECS/Fargate**: For scalable production deployment
4. **AWS Amplify**: For frontend-only deployment

Detailed instructions are available in the [Deployment Guide](DEPLOYMENT.md).

### How much does it cost to run S4?

The cost depends on your deployment method and scale:

- **Self-hosted**: Free, but you'll need to provide infrastructure
- **AWS**: Costs will include:
  - EC2 or Fargate instances (from ~$30/month)
  - S3 storage ($0.023 per GB)
  - Data transfer costs
  - OpenAI API costs (varies by usage)

A typical small deployment might cost $50-100/month on AWS.

### Do I need an OpenAI API key?

Yes, S4 uses OpenAI's embedding models to generate vector representations of documents and queries. You'll need to obtain an API key from OpenAI and configure it in your S4 deployment.

### Can I deploy S4 on-premises?

Yes, S4 can be deployed on-premises using Docker Compose or Kubernetes. You'll need to provide:
- Compute resources
- Storage (can use MinIO as an S3-compatible alternative)
- Network connectivity for the OpenAI API

### How do I scale S4 for production use?

To scale S4:
1. Use a production-ready deployment on AWS ECS/Fargate
2. Configure auto-scaling based on CPU/memory usage
3. Use RDS for the metadata database
4. Consider using a managed vector database for large-scale deployments
5. Implement a CDN for the frontend
6. Set up proper monitoring and alerting

## Administration Questions

### How do I create and manage tenants?

Tenants can be managed through:
1. The Admin Portal web interface
2. The Admin API endpoints

To create a tenant, you'll need:
- Tenant name
- Contact email
- Company name
- Subscription plan

### What subscription plans are available by default?

S4 comes with these default plans:
- **Basic**: Limited storage and API calls
- **Standard**: Moderate storage and API calls
- **Premium**: High storage and API calls
- **Enterprise**: Custom limits

You can modify these plans or create custom plans.

### How do I monitor system usage?

S4 provides monitoring through:
- Admin Portal dashboard with usage metrics
- API endpoints for usage statistics
- Logs (can be integrated with CloudWatch, ELK Stack, etc.)
- Health check endpoints

### How do I backup S4 data?

For a complete backup:
1. Backup the S3 bucket containing documents
2. Backup the metadata database
3. Export tenant configurations
4. Keep a copy of environment variables

For AWS deployments, you can use AWS Backup to automate this process.

## Security Questions

### How secure is S4?

S4 is designed with security in mind:
- API key authentication
- Proper tenant isolation
- Data encryption at rest and in transit
- Secure default configurations
- Regular security updates

For production deployments, follow the security best practices in the [Security Guide](SECURITY.md).

### How are API keys managed?

- **Admin API Key**: Generated during deployment, should be stored securely
- **Tenant API Keys**: Generated when creating tenants, managed through the Admin Portal
- All keys should be rotated periodically for security

### Is data encrypted?

Yes, S4 encrypts data:
- In transit using HTTPS
- At rest using S3 server-side encryption
- API keys and sensitive configuration using secure storage

### How does S4 handle authentication?

S4 uses API key-based authentication:
- Tenants authenticate with their tenant API key
- Administrators authenticate with the Admin API key
- All API requests require valid authentication

## Usage Questions

### How do users search documents?

Users can search using:
1. The frontend UI search interface
2. The REST API for programmatic access

The search query is converted to an embedding and matched against document embeddings to find semantically similar content.

### What search features does S4 support?

S4 supports:
- Semantic (vector) search
- Metadata filtering
- Result ranking by relevance
- Customizable search parameters
- Result highlighting
- Pagination

### Can I customize the user interface?

Yes, the React frontend can be customized:
- White-labeling with your brand
- CSS customization
- Component modifications
- Adding new features

### How many documents can S4 handle?

The document capacity depends on:
- Your infrastructure resources
- The vector database implementation
- Document size and complexity

A typical deployment can handle millions of document chunks. For larger scales, consider a distributed vector database.

## Support and Troubleshooting

### How do I get support for S4?

Support options include:
- [GitHub Issues](https://github.com/your-org/s4/issues) for bug reports
- Documentation including the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Community forums
- Commercial support options (contact sales@your-org.com)

### What should I do if I encounter an error?

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review application logs for error messages
3. Check the system requirements
4. Search for similar issues on GitHub
5. Submit a detailed bug report if needed

### How do I report a security vulnerability?

If you discover a security vulnerability:
1. Do NOT disclose it publicly
2. Email security@your-org.com with details
3. Follow responsible disclosure practices

### How do I update S4?

To update S4:
1. Check the release notes for changes
2. Backup your current deployment
3. Update the code (git pull or download)
4. Update dependencies
5. Run database migrations if needed
6. Restart services

## Contributing Questions

### How can I contribute to S4?

You can contribute by:
- Submitting bug reports
- Creating feature requests
- Contributing code via pull requests
- Improving documentation
- Sharing your experience in the community

See the [Contributing Guide](CONTRIBUTING.md) for details.

### What's the roadmap for S4?

Upcoming features include:
- Hybrid search (combining semantic and keyword search)
- Additional document formats
- Enhanced analytics
- Custom embedding models
- Advanced visualization features
- Improved scalability
- Additional deployment options

Check the project's GitHub for the latest roadmap.

## Additional Questions

If your question isn't answered here, please:
- Check the full documentation
- Search for answers in GitHub issues
- Ask in the community forum
- Contact support@your-org.com 