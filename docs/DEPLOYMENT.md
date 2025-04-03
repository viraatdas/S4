# S4 Deployment Guide

This guide provides detailed instructions for deploying the S4 Semantic Search Service in various environments.

## Deployment Options

S4 can be deployed using several methods:

1. **Docker Compose** (local development and testing)
2. **AWS Elastic Beanstalk** (production)
3. **AWS ECS/Fargate** (production, scalable)
4. **AWS Amplify** (frontend only)

## Prerequisites

- Docker and Docker Compose (for local deployment)
- AWS CLI (for AWS deployments)
- Node.js 16+ (for frontend development)
- Python 3.9+ (for backend development)
- An OpenAI API key
- AWS account with appropriate permissions

## Local Deployment with Docker Compose

The simplest way to deploy S4 locally is using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/s4.git
   cd s4
   ```

2. Run the deployment script:
   ```bash
   ./deploy_docker.sh
   ```

3. Follow the prompts to enter:
   - S3 bucket name
   - AWS region
   - OpenAI API key
   - Admin API key (or let it generate one)

4. The script will:
   - Create configuration files
   - Build and start Docker containers
   - Provide instructions for accessing the application

5. Access the application:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost
   - Admin Portal: http://localhost/admin/login

## AWS Elastic Beanstalk Deployment

For a production deployment on AWS Elastic Beanstalk:

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Create an S3 bucket for document storage:
   ```bash
   aws s3 mb s3://your-s4-bucket --region your-region
   ```

3. Run the Elastic Beanstalk deployment script:
   ```bash
   ./deploy_beanstalk.sh
   ```

4. Follow the prompts to enter:
   - S3 bucket name
   - AWS region
   - OpenAI API key
   - Admin API key
   - EB environment name

5. The script will:
   - Create an Elastic Beanstalk environment
   - Deploy the backend API
   - Deploy the frontend to S3 + CloudFront
   - Configure environment variables

6. Access your application using the provided URLs.

## AWS ECS/Fargate Deployment

For a scalable production deployment on AWS ECS/Fargate:

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Create an S3 bucket for document storage:
   ```bash
   aws s3 mb s3://your-s4-bucket --region your-region
   ```

3. Run the ECS deployment script:
   ```bash
   ./deploy_ecs.sh
   ```

4. Follow the prompts to enter:
   - S3 bucket name
   - AWS region
   - OpenAI API key
   - Admin API key
   - VPC and subnet details
   - Load balancer configuration

5. The script will:
   - Create ECR repositories
   - Build and push Docker images
   - Create ECS task definitions and services
   - Set up Application Load Balancer
   - Configure environment variables

6. Access your application using the provided URLs.

## Manual Configuration

If you prefer to configure the deployment manually:

### Backend Configuration (.env file)

```
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# S3 Configuration
S4_S3_BUCKET=your_s3_bucket_name
S4_S3_REGION=your_aws_region

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Multi-tenant settings
S4_DISABLE_API_AUTH=false
S4_ADMIN_API_KEY=your_admin_api_key

# API settings
S4_API_HOST=0.0.0.0
S4_API_PORT=8000
S4_CORS_ORIGINS=*

# Optional settings
S4_DEBUG=false
S4_DATA_DIR=/app/data
S4_EMBEDDING_MODEL=text-embedding-3-small
```

### Frontend Configuration (s4-ui/.env file)

```
REACT_APP_API_URL=https://your-api-endpoint.com/api
```

## Post-Deployment Steps

After deploying S4, you need to:

1. Create your first tenant:
   ```bash
   curl -X POST https://your-api-url/api/admin/tenants \
     -H "X-Admin-Key: your-admin-key" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Example Company",
       "email": "admin@example.com",
       "company": "Example Inc",
       "plan_id": "basic"
     }'
   ```

2. Access the Admin Portal:
   - Navigate to `https://your-frontend-url/admin/login`
   - Log in using your Admin API key
   - Use the Admin Portal to manage tenants and monitor system usage

3. Test the tenant access:
   - Use the tenant API key returned from the creation step
   - Log in to the frontend UI with this key

## Environment Variables

Here's a complete list of environment variables you can configure:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| AWS_ACCESS_KEY_ID | AWS access key | - | Yes |
| AWS_SECRET_ACCESS_KEY | AWS secret key | - | Yes |
| S4_S3_BUCKET | S3 bucket name for storage | - | Yes |
| S4_S3_REGION | AWS region for S3 bucket | us-east-1 | Yes |
| OPENAI_API_KEY | OpenAI API key | - | Yes |
| S4_ADMIN_API_KEY | Admin API key | Random | Yes |
| S4_API_HOST | Host to bind API server | 0.0.0.0 | No |
| S4_API_PORT | Port for API server | 8000 | No |
| S4_CORS_ORIGINS | Allowed CORS origins | * | No |
| S4_DEBUG | Enable debug mode | false | No |
| S4_DATA_DIR | Directory for local data | /app/data | No |
| S4_EMBEDDING_MODEL | OpenAI embedding model | text-embedding-3-small | No |
| S4_DISABLE_API_AUTH | Disable API auth (development only) | false | No |

## Troubleshooting

### Common Issues

1. **S3 Access Problems**
   - Check AWS credentials
   - Verify bucket exists and permissions are correct
   - Ensure bucket policy allows necessary actions

2. **API Connection Issues**
   - Check CORS settings
   - Verify network connectivity between frontend and backend
   - Check load balancer health checks

3. **Authentication Problems**
   - Verify Admin API key is correctly set
   - Check tenant API keys are valid
   - Ensure environment variables are correctly set

### Logs

- **Docker Compose**: `docker-compose logs s4` or `docker-compose logs s4-ui`
- **Elastic Beanstalk**: Check logs in AWS Console or use `eb logs`
- **ECS/Fargate**: Check CloudWatch logs for the service

## Updating S4

To update S4 to a new version:

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Re-run the deployment script for your environment.

## Security Considerations

1. **API Keys**: Store API keys securely; never commit them to your repository
2. **Admin Access**: The admin key provides full access to all tenant data; keep it secure
3. **S3 Storage**: Configure appropriate bucket policies
4. **Network Security**: Use VPC, security groups, and network ACLs for AWS deployments
5. **HTTPS**: Always use HTTPS in production

## Support and Community

- GitHub Issues: https://github.com/your-org/s4/issues
- Documentation: https://your-org.github.io/s4
- Community Forum: https://community.your-org.com/s4

## License

S4 is licensed under the MIT License. See the LICENSE file for details. 