# S4 AWS Deployment Guide

This guide explains how to deploy the S4 semantic search service to AWS using different deployment options.

## Deployment Scripts

We've created two deployment scripts to simplify the deployment process:

1. `deploy_aws.sh` - Deploy to AWS Elastic Beanstalk
2. `deploy_ecs.sh` - Deploy to AWS ECS using Docker containers

Both scripts automatically:
- Create required AWS resources (S3 bucket, ECR repository, ECS cluster, etc.)
- Set up the appropriate environment configuration
- Deploy the application to the chosen platform
- Provide instructions for accessing the deployed service

## Option 1: AWS Elastic Beanstalk

Elastic Beanstalk is a simple way to deploy and scale web applications. It's ideal for getting started quickly with minimal configuration.

### Prerequisites:
- AWS CLI installed
- AWS EB CLI installed (will be installed by the script if not present)
- Docker installed (for building the application package)

### Deployment Steps:

1. Make the deployment script executable (if not already):
   ```bash
   chmod +x deploy_aws.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy_aws.sh
   ```

3. When prompted, provide the following information:
   - S3 bucket name for storing S4 data
   - OpenAI API key for embeddings
   - Admin API key (or let the script generate one)

4. The script will create the necessary AWS resources and deploy the application.

5. After deployment completes, the script will display the URL for accessing your S4 service.

### Elastic Beanstalk Benefits:
- Simple deployment and scaling
- Managed platform updates
- Health monitoring and reporting
- Integration with other AWS services

## Option 2: AWS ECS (Docker Containers)

ECS (Elastic Container Service) provides more control and scalability for containerized applications. This option is better for production deployments that require fine-grained control.

### Prerequisites:
- AWS CLI installed
- Docker installed

### Deployment Steps:

1. Make the deployment script executable (if not already):
   ```bash
   chmod +x deploy_ecs.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy_ecs.sh
   ```

3. When prompted, provide the following information:
   - S3 bucket name for storing S4 data
   - OpenAI API key for embeddings
   - Admin API key (or let the script generate one)

4. The script will:
   - Create an ECR repository for the Docker image
   - Build and push the Docker image
   - Create an ECS cluster
   - Set up a load balancer and target group
   - Deploy the ECS service using Fargate (serverless containers)

5. After deployment completes, the script will display the load balancer URL for accessing your S4 service.

### ECS Benefits:
- Container-based deployment
- Better scaling capabilities
- More control over infrastructure
- Integration with AWS application load balancers
- CloudWatch integration for monitoring

## AWS Credentials

Both deployment scripts use the following AWS credentials from your environment:

- AWS_ACCESS_KEY_ID: AKIAYWBJYKWSBG5VEIJP
- AWS_SECRET_ACCESS_KEY: [REDACTED]
- AWS_DEFAULT_REGION: us-east-1

These credentials must have permissions to:
- Create and manage S3 buckets
- Create and manage Elastic Beanstalk applications (for EB deployment)
- Create and manage ECR repositories, ECS clusters, and related resources (for ECS deployment)

## Post-Deployment Steps

After deployment, you should:

1. Create a tenant through the Admin API:
   ```bash
   curl -X POST https://your-service-url/api/admin/tenants \
     -H "X-Admin-Key: YOUR_ADMIN_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Example Company",
       "email": "admin@example.com",
       "company": "Example Inc",
       "plan_id": "basic"
     }'
   ```

2. The response will include a tenant auth key that can be used to access the S4 API.

3. Access the API documentation at `https://your-service-url/docs`

## Monitoring and Scaling

For information on monitoring and scaling S4 in production, refer to the [MONITORING.md](MONITORING.md) guide.

## Security Considerations

For production deployments, consider:

1. Setting up HTTPS using AWS Certificate Manager
2. Implementing proper IAM roles instead of using access keys
3. Setting up proper VPC networking for ECS deployments
4. Implementing AWS WAF for web application firewall capabilities
5. Setting up CloudTrail for auditing AWS API calls

## Troubleshooting

If you encounter issues during deployment:

1. For Elastic Beanstalk:
   - Check EB logs: `eb logs`
   - SSH into the instance: `eb ssh`

2. For ECS:
   - Check CloudWatch logs for the ECS service
   - Check ECS service events: `aws ecs describe-services --cluster s4-cluster --services s4-service`

3. Check S3 bucket permissions if you encounter storage issues

4. Verify that your AWS credentials have the necessary permissions 