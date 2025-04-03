#!/bin/bash
# S4 Deployment Script for AWS Elastic Beanstalk
set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== S4 AWS Elastic Beanstalk Deployment Script =====${NC}"
echo -e "This script will deploy S4 to AWS Elastic Beanstalk"
echo ""

# Check required tools
if ! command -v eb &> /dev/null; then
    echo -e "${YELLOW}Installing AWS EB CLI...${NC}"
    pip install awsebcli
fi

if ! command -v zip &> /dev/null; then
    echo -e "${RED}Error: zip command not found. Please install it first.${NC}"
    exit 1
fi

# Prompt for required information
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

# Create the .ebextensions directory if it doesn't exist
if [ ! -d ".ebextensions" ]; then
    mkdir -p .ebextensions
fi

# Create the configuration file
cat > .ebextensions/01_s4.config << EOL
option_settings:
  aws:elasticbeanstalk:application:environment:
    S4_S3_BUCKET: $S4_S3_BUCKET
    S4_S3_REGION: \${AWS::Region}
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

# Create .ebignore file to control what gets deployed
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
deploy.sh
deploy_aws.sh
deploy_to_ecs.sh
deploy_to_eb.sh
secure_deploy.sh

# Frontend code (will be deployed separately)
s4-ui/
EOL

# Initialize the EB application
echo "Initializing Elastic Beanstalk application..."
eb init $APP_NAME -p python-3.9 --region us-east-1

# Create/deploy the application
echo "Creating Elastic Beanstalk environment and deploying application..."
eb create $ENV_NAME --envvars "S4_ADMIN_API_KEY=$S4_ADMIN_API_KEY"

# Get the application URL
APP_URL=$(eb status $ENV_NAME | grep CNAME | awk '{print $2}')

# Now deploy the frontend to S3
echo ""
echo -e "${BLUE}Deploying frontend to S3...${NC}"

# Create S3 bucket for UI if it doesn't exist
UI_BUCKET_NAME="s4-ui-$S4_S3_BUCKET"
if ! aws s3 ls "s3://$UI_BUCKET_NAME" 2>&1 > /dev/null; then
    echo "Creating S3 bucket for UI: $UI_BUCKET_NAME"
    aws s3 mb "s3://$UI_BUCKET_NAME" --region us-east-1
    
    # Enable static website hosting
    aws s3 website "s3://$UI_BUCKET_NAME" --index-document index.html --error-document index.html
    
    # Create bucket policy to allow public access
    POLICY="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"PublicReadGetObject\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$UI_BUCKET_NAME/*\"}]}"
    aws s3api put-bucket-policy --bucket "$UI_BUCKET_NAME" --policy "$POLICY"
fi

# Build the frontend
cd s4-ui

# Configure API URL
echo "REACT_APP_API_URL=http://$APP_URL/api" > .env.production

# Install dependencies and build
echo "Installing UI dependencies..."
npm install

echo "Building UI application..."
npm run build

# Upload to S3
echo "Uploading UI files to S3..."
aws s3 sync build/ "s3://$UI_BUCKET_NAME" --delete

# Get the website URL
UI_URL="http://$UI_BUCKET_NAME.s3-website.us-east-1.amazonaws.com"

cd ..

echo -e "${GREEN}===== Deployment Complete =====${NC}"
echo "S4 Backend API: http://$APP_URL"
echo "S4 Frontend UI: $UI_URL"
echo "Admin API key: $S4_ADMIN_API_KEY"
echo ""
echo "To create your first tenant, use:"
echo "curl -X POST http://$APP_URL/api/admin/tenants \\"
echo "  -H \"X-Admin-Key: $S4_ADMIN_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
echo ""
echo -e "${YELLOW}Important Notes:${NC}"
echo "1. It may take a few minutes for the services to fully initialize."
echo "2. For production use, consider setting up a CloudFront distribution for the frontend."
echo "3. To set up a custom domain, configure Route 53 and update the frontend configuration." 