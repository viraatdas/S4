#!/bin/bash
# S4 Deployment Script for AWS Amplify
set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== S4 AWS Amplify Deployment Script =====${NC}"
echo -e "This script will deploy the S4 UI to AWS Amplify and the backend to AWS Elastic Beanstalk"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not found. Please install it first:${NC}"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check AWS credentials
echo "Testing AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials are invalid or not configured.${NC}"
    echo "Please update your AWS credentials in ~/.aws/credentials"
    echo "To create new access keys, go to:"
    echo "AWS Console > IAM > Users > [your-user] > Security credentials > Create access key"
    exit 1
fi

# Get AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    AWS_REGION="us-east-1"
    aws configure set region $AWS_REGION
fi

echo -e "${GREEN}Using AWS Account: $AWS_ACCOUNT_ID in region: $AWS_REGION${NC}"

# Collect required information
S4_S3_BUCKET=""
OPENAI_API_KEY=""
S4_ADMIN_API_KEY=""
APP_NAME="s4-service"
ENV_NAME="production"

read -p "Enter S3 bucket name for S4 storage (lowercase, no spaces): " S4_S3_BUCKET
read -p "Enter OpenAI API key: " OPENAI_API_KEY

# Generate admin key if not provided
read -p "Enter secure admin API key (or press enter to generate one): " S4_ADMIN_API_KEY
if [ -z "$S4_ADMIN_API_KEY" ]; then
    S4_ADMIN_API_KEY=$(openssl rand -hex 16)
    echo "Generated Admin API Key: $S4_ADMIN_API_KEY"
    echo "IMPORTANT: Save this key securely!"
fi

# 1. CREATE S3 BUCKET
echo -e "${BLUE}Step 1: Creating S3 bucket for S4 storage...${NC}"
if ! aws s3 ls "s3://$S4_S3_BUCKET" 2>&1 > /dev/null; then
    echo "Creating S3 bucket: $S4_S3_BUCKET"
    aws s3 mb "s3://$S4_S3_BUCKET" --region $AWS_REGION
    
    # Set security best practices
    aws s3api put-public-access-block \
        --bucket $S4_S3_BUCKET \
        --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
    
    echo "S3 bucket created successfully."
else
    echo "S3 bucket already exists."
fi

# 2. DEPLOY BACKEND to Elastic Beanstalk
echo -e "${BLUE}Step 2: Deploying backend to Elastic Beanstalk...${NC}"

# Create the .ebextensions directory if it doesn't exist
if [ ! -d ".ebextensions" ]; then
    mkdir -p .ebextensions
fi

# Create the configuration file
cat > .ebextensions/01_s4.config << EOL
option_settings:
  aws:elasticbeanstalk:application:environment:
    S4_S3_BUCKET: $S4_S3_BUCKET
    S4_S3_REGION: $AWS_REGION
    OPENAI_API_KEY: $OPENAI_API_KEY
    S4_DISABLE_API_AUTH: false
    S4_ADMIN_API_KEY: $S4_ADMIN_API_KEY
    S4_API_HOST: 0.0.0.0
    S4_API_PORT: 8080
    S4_CORS_ORIGINS: "*"
    S4_DEBUG: false
    S4_DATA_DIR: /var/app/current/data
    PYTHONPATH: /var/app/current

container_commands:
  01_create_data_dirs:
    command: "mkdir -p /var/app/current/data/indices /var/app/current/data/tenants /var/app/current/data/temp"
  02_initialize_service:
    command: "cd /var/app/current && python -m s4 init"
EOL

# Create the Procfile
echo "Creating Procfile..."
cat > Procfile << EOL
web: python -m s4 start --host=0.0.0.0 --port=8080
EOL

# Create .ebignore file
echo "Creating .ebignore file..."
cat > .ebignore << EOL
# Python files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.pytest_cache/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Local development
.env
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Local data files
data/
*.faiss
*.pickle

# Deployment scripts
deploy*.sh
*.sh

# Frontend code
s4-ui/
EOL

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt..."
    pip freeze > requirements.txt
fi

# Initialize EB
echo "Initializing Elastic Beanstalk application..."
if ! command -v eb &> /dev/null; then
    echo -e "${YELLOW}Installing EB CLI...${NC}"
    pip install awsebcli
fi

eb init $APP_NAME -p python-3.9 --region $AWS_REGION
echo "Creating/deploying Elastic Beanstalk environment..."
eb create $ENV_NAME --envvars "S4_ADMIN_API_KEY=$S4_ADMIN_API_KEY"

# Get the backend URL
BACKEND_URL=$(eb status $ENV_NAME | grep CNAME | awk '{print $2}')
echo -e "${GREEN}Backend deployed at: http://$BACKEND_URL${NC}"

# 3. DEPLOY FRONTEND to Amplify
echo -e "${BLUE}Step 3: Deploying frontend to Amplify...${NC}"

# Build the frontend
cd s4-ui

# Create .env.production with the API URL
echo "Creating production environment for the frontend..."
echo "REACT_APP_API_URL=http://$BACKEND_URL/api" > .env.production

# Create amplify.yml for the build configuration
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

# Create a deployment package
echo "Creating deployment package..."
zip -r ../s4-ui-deploy.zip .

cd ..

# Create/update Amplify app
echo "Creating/updating Amplify app..."
APP_ID=$(aws amplify list-apps --query "apps[?name=='s4-ui'].appId" --output text)

if [ -z "$APP_ID" ]; then
    echo "Creating new Amplify app..."
    APP_ID=$(aws amplify create-app --name s4-ui --query "app.appId" --output text)
    echo "App created with ID: $APP_ID"
else
    echo "Using existing Amplify app with ID: $APP_ID"
fi

# Create a branch
echo "Creating/updating main branch in Amplify..."
aws amplify create-branch --app-id $APP_ID --branch-name main || true

# Deploy
echo "Deploying frontend to Amplify..."
JOB_ID=$(aws amplify start-deployment --app-id $APP_ID --branch-name main --source-url s4-ui-deploy.zip --query "jobId" --output text)

echo "Deployment started with Job ID: $JOB_ID"
echo "Waiting for deployment to complete..."

# Poll for deployment status
STATUS="PENDING"
while [ "$STATUS" == "PENDING" ] || [ "$STATUS" == "RUNNING" ]; do
    sleep 10
    STATUS=$(aws amplify get-job --app-id $APP_ID --branch-name main --job-id $JOB_ID --query "job.summary.status" --output text)
    echo "Deployment status: $STATUS"
done

# Get frontend URL
FRONTEND_URL=$(aws amplify get-app --app-id $APP_ID --query "app.defaultDomain" --output text)

# Finalization
echo -e "${GREEN}===== Deployment Complete =====${NC}"
echo "Backend API: http://$BACKEND_URL"
echo "Frontend UI: https://$FRONTEND_URL"
echo "Admin API key: $S4_ADMIN_API_KEY"
echo ""
echo "To create your first tenant, use:"
echo "curl -X POST http://$BACKEND_URL/api/admin/tenants \\"
echo "  -H \"X-Admin-Key: $S4_ADMIN_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Create a tenant using the command above"
echo "2. Use the returned tenant key to log in to the frontend UI"
echo "3. For a custom domain, configure Route 53 and update in Amplify Console"
echo ""
echo -e "${YELLOW}Admin Portal Access:${NC}"
echo "1. Access the Admin Portal at: https://$FRONTEND_URL/admin/login"
echo "2. Log in using your Admin API key: $S4_ADMIN_API_KEY"
echo "3. You can manage tenants, subscriptions, and view system data directly through the UI"
echo ""
echo -e "${GREEN}Thank you for deploying S4!${NC}" 