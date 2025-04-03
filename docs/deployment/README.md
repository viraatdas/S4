# S4 Cloud Deployment Guide

This guide provides instructions for deploying the S4 service to various cloud platforms.

## Prerequisites

Before deploying S4 to any cloud platform, you need:

1. AWS credentials with S3 permissions
2. An S3 bucket for storage
3. An OpenAI API key
4. Your S4 codebase ready for deployment

## Option 1: AWS Elastic Beanstalk

AWS Elastic Beanstalk provides an easy way to deploy and scale web applications.

### Steps:

1. Install the AWS EB CLI tool:
   ```
   pip install awsebcli
   ```

2. Initialize your EB application:
   ```
   eb init -p python-3.9 s4-service
   ```

3. Create an Elastic Beanstalk environment file `.ebextensions/01_s4.config`:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       AWS_ACCESS_KEY_ID: REPLACE_WITH_YOUR_KEY
       AWS_SECRET_ACCESS_KEY: REPLACE_WITH_YOUR_SECRET
       S4_S3_BUCKET: your-s4-bucket
       S4_S3_REGION: us-east-1
       OPENAI_API_KEY: REPLACE_WITH_YOUR_KEY
       S4_DISABLE_API_AUTH: false
       S4_ADMIN_API_KEY: REPLACE_WITH_YOUR_SECURE_KEY
       S4_API_HOST: 0.0.0.0
       S4_API_PORT: 8080
       S4_CORS_ORIGINS: "*"
       S4_DEBUG: false
       S4_DATA_DIR: /var/app/current/data
   
   container_commands:
     01_create_data_dirs:
       command: "mkdir -p /var/app/current/data/indices /var/app/current/data/tenants /var/app/current/data/temp"
     02_initialize_service:
       command: "python -m s4 init"
   ```

4. Create a `Procfile` for Elastic Beanstalk:
   ```
   web: python -m s4 start --host=0.0.0.0 --port=8080
   ```

5. Deploy the application:
   ```
   eb create s4-production
   ```

6. After deployment, your service will be accessible at the provided EB URL.

## Option 2: AWS ECS (Docker Deployment)

AWS ECS allows you to run containerized applications on a cluster.

### Steps:

1. Create an ECR repository for your container image:
   ```
   aws ecr create-repository --repository-name s4-service
   ```

2. Build and push your Docker image:
   ```
   # Login to ECR
   aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
   
   # Build image
   docker build -t s4-service .
   
   # Tag image
   docker tag s4-service:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/s4-service:latest
   
   # Push image
   docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/s4-service:latest
   ```

3. Create an ECS task definition (see AWS documentation)

4. Create an ECS service using the task definition

5. Set up a load balancer to expose your service

## Option 3: Google Cloud Run

Google Cloud Run is a fully managed platform for containerized applications.

### Steps:

1. Install Google Cloud SDK

2. Build and push your Docker image:
   ```
   # Build the container
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/s4-service
   ```

3. Deploy to Cloud Run:
   ```
   gcloud run deploy s4-service \
     --image gcr.io/YOUR_PROJECT_ID/s4-service \
     --platform managed \
     --allow-unauthenticated \
     --memory 2G \
     --set-env-vars="AWS_ACCESS_KEY_ID=YOUR_KEY,AWS_SECRET_ACCESS_KEY=YOUR_SECRET,S4_S3_BUCKET=your-s4-bucket,S4_S3_REGION=us-east-1,OPENAI_API_KEY=YOUR_KEY,S4_DISABLE_API_AUTH=false,S4_ADMIN_API_KEY=YOUR_SECURE_KEY,S4_DATA_DIR=/tmp"
   ```

4. For persistent storage, consider mounting a Google Cloud Storage bucket

## Option 4: Azure App Service

Azure App Service provides a platform for hosting web applications.

### Steps:

1. Create an Azure App Service plan

2. Create a Web App for Containers

3. Configure environment variables in the Application settings

4. Set up continuous deployment from your container registry

## Multi-Tenant Considerations

When deploying S4 as a multi-tenant service, consider:

1. **Data Isolation**: Ensure tenant data is properly isolated in S3
2. **Security**: Use a strong, random admin API key
3. **Monitoring**: Set up monitoring for tenant usage
4. **Scalability**: Consider using autoscaling based on usage metrics
5. **Backups**: Implement regular backups of tenant data

## Managing Tenants

Once deployed, you can manage tenants using the Admin API:

```bash
# Create a new tenant
curl -X POST https://your-deployed-service.com/api/admin/tenants \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Example Company", "email": "admin@example.com", "company": "Example Inc", "plan_id": "basic"}'

# List all tenants
curl -X GET https://your-deployed-service.com/api/admin/tenants \
  -H "X-Admin-Key: YOUR_ADMIN_KEY"
```

Each tenant will receive a unique auth key that they can use to access the S4 API. 