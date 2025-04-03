#!/bin/bash
# S4 Frontend-only Deployment Script for AWS Amplify
set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== S4 Frontend Deployment Script =====${NC}"
echo -e "This script will deploy the S4 UI to AWS Amplify"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

# Set the AWS region
AWS_REGION="us-east-1"
aws configure set region $AWS_REGION

# Get AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)

# Set the backend URL and admin API key
BACKEND_URL="http://s4-prod-20250323.eba-ermuim2e.us-east-1.elasticbeanstalk.com"
ADMIN_API_KEY="s4_admin_key_1ecdaf19804e95d3"

echo "Using backend URL: $BACKEND_URL"
echo "Using Admin API Key: $ADMIN_API_KEY"
echo "IMPORTANT: Save this key securely!"

# Create a production environment file
echo "Creating production environment file..."
cat > s4-ui/.env.production << EOL
REACT_APP_API_URL=${BACKEND_URL}/api
REACT_APP_ADMIN_API_KEY=${ADMIN_API_KEY}
EOL

# Create Amplify.yml file
echo "Creating Amplify configuration file..."
cat > amplify.yml << EOL
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: build
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
EOL

# Navigate to the UI directory
cd s4-ui

# Build the React app
echo "Building the React app..."
npm ci
npm run build

# Create deployment zip
echo "Creating deployment zip..."
cd build
zip -r ../../s4-ui-deploy.zip .
cd ../..

# Create S3 bucket for deployment files if it doesn't exist
TIMESTAMP=$(date +%s)
BUCKET_NAME="s4-frontend-deployment-$TIMESTAMP"
echo "Creating S3 bucket for deployment: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME

# Add bucket policy to allow Amplify to read the deployment file
echo "Setting bucket policy to allow Amplify access..."
cat > bucket-policy.json << EOL
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAmplifyService",
      "Effect": "Allow",
      "Principal": {
        "Service": "amplify.amazonaws.com"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${BUCKET_NAME}",
        "arn:aws:s3:::${BUCKET_NAME}/*"
      ]
    }
  ]
}
EOL

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

# Upload the zip to S3
echo "Uploading frontend zip to S3..."
aws s3 cp s4-ui-deploy.zip s3://$BUCKET_NAME/s4-ui-deploy.zip

# Create or update Amplify app
APP_NAME="s4-frontend"
EXISTING_APP=$(aws amplify list-apps --query "apps[?name=='$APP_NAME'].appId" --output text)

if [ -z "$EXISTING_APP" ] || [ "$EXISTING_APP" == "None" ]; then
    echo "Creating new Amplify app..."
    APP_ID=$(aws amplify create-app --name $APP_NAME --query "app.appId" --output text)
else
    echo "Using existing Amplify app..."
    APP_ID=$EXISTING_APP
fi

# Try to update the branch first, create it if it doesn't exist
aws amplify update-branch --app-id $APP_ID --branch-name main 2>/dev/null || \
aws amplify create-branch --app-id $APP_ID --branch-name main

# Start the deployment with the correct S3 URL format
echo "Starting deployment to Amplify..."
JOB_ID=$(aws amplify start-deployment --app-id $APP_ID --branch-name main --source-url "s3://$BUCKET_NAME/s4-ui-deploy.zip" --query "jobId" --output text)

echo "Deployment started with Job ID: $JOB_ID"
echo "Once deployed, you can access the application at: https://main.$APP_ID.amplifyapp.com"
echo "To create a tenant, visit the admin portal at: https://main.$APP_ID.amplifyapp.com/admin"
echo "Use the admin key '$ADMIN_API_KEY' to log in to the admin portal."

# Finalization
echo -e "${GREEN}===== Deployment Complete =====${NC}"
echo "Backend API: http://$BACKEND_URL"
echo "Frontend UI: https://main.$APP_ID.amplifyapp.com"
echo "Admin API key: $ADMIN_API_KEY"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Create a tenant using the command above"
echo "2. Use the returned tenant key to log in to the frontend UI"
echo "3. For a custom domain, configure Route 53 and update in Amplify Console"
echo ""
echo -e "${YELLOW}Admin Portal Access:${NC}"
echo "1. Access the Admin Portal at: https://main.$APP_ID.amplifyapp.com/admin"
echo "2. Log in using your Admin API key: $ADMIN_API_KEY"
echo "3. You can manage tenants, subscriptions, and view system data directly through the UI"
echo ""
echo -e "${GREEN}Thank you for deploying S4!${NC}" 