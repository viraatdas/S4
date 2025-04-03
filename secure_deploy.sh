#!/bin/bash
# Secure S4 Deployment Script for AWS
set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== S4 Secure AWS Deployment Script =====${NC}"
echo -e "This script will deploy both the S4 backend and UI to AWS"
echo ""

# Check AWS CLI installation
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html for installation instructions."
    exit 1
fi

# Check if aws credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${YELLOW}AWS credentials not configured. Setting them up now...${NC}"
    aws configure
fi

# Get AWS account details
echo "Verifying AWS credentials..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    read -p "Enter AWS region (e.g., us-east-1): " AWS_REGION
    aws configure set region $AWS_REGION
fi

echo -e "${GREEN}Using AWS Account: $AWS_ACCOUNT_ID in region: $AWS_REGION${NC}"

# Prompt for required information
S4_S3_BUCKET=""
OPENAI_API_KEY=""
S4_ADMIN_API_KEY=""
UI_BUCKET_NAME=""

read -p "Enter S3 bucket name for S4 storage (lowercase, no spaces): " S4_S3_BUCKET
read -p "Enter S3 bucket name for UI hosting (lowercase, no spaces): " UI_BUCKET_NAME
read -p "Enter OpenAI API key: " OPENAI_API_KEY

# Generate admin key if not provided
read -p "Enter secure admin API key (or press enter to generate one): " S4_ADMIN_API_KEY
if [ -z "$S4_ADMIN_API_KEY" ]; then
    S4_ADMIN_API_KEY=$(openssl rand -hex 16)
    echo "Generated Admin API Key: $S4_ADMIN_API_KEY"
    echo "IMPORTANT: Save this key securely!"
fi

# Ask for deployment type
echo ""
echo "Select backend deployment type:"
echo "1) AWS Elastic Beanstalk (recommended for simplicity)"
echo "2) AWS ECS (more robust, production-ready)"
read -p "Enter selection (1 or 2): " DEPLOYMENT_SELECTION

if [ "$DEPLOYMENT_SELECTION" = "1" ]; then
    DEPLOYMENT_TYPE="eb"
    echo -e "${GREEN}Selected: AWS Elastic Beanstalk${NC}"
    
    # Check if EB CLI is installed
    if ! command -v eb &> /dev/null; then
        echo -e "${YELLOW}Installing AWS EB CLI...${NC}"
        pip install awsebcli
    fi
    
elif [ "$DEPLOYMENT_SELECTION" = "2" ]; then
    DEPLOYMENT_TYPE="ecs"
    echo -e "${GREEN}Selected: AWS ECS${NC}"
else
    echo -e "${RED}Invalid selection. Exiting.${NC}"
    exit 1
fi

# ===== BACKEND DEPLOYMENT =====
echo ""
echo -e "${BLUE}Starting S4 backend deployment...${NC}"

# Create S3 bucket for storage if it doesn't exist
echo "Checking S3 bucket for storage..."
if ! aws s3 ls "s3://$S4_S3_BUCKET" 2>&1 > /dev/null; then
    echo "Creating S3 bucket for storage: $S4_S3_BUCKET"
    aws s3 mb "s3://$S4_S3_BUCKET" --region $AWS_REGION
    
    # Set security best practices
    aws s3api put-public-access-block \
        --bucket $S4_S3_BUCKET \
        --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
fi

# Deploy backend based on selected method
if [ "$DEPLOYMENT_TYPE" = "eb" ]; then
    # Elastic Beanstalk Deployment
    
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

container_commands:
  01_create_data_dirs:
    command: "mkdir -p /var/app/current/data/indices /var/app/current/data/tenants /var/app/current/data/temp"
  02_initialize_service:
    command: "python -m s4 init"
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
deploy_ecs.sh
deploy_full.sh
secure_deploy.sh
EOL

    # Initialize the EB application
    echo "Initializing Elastic Beanstalk application..."
    APP_NAME="s4-service"
    ENV_NAME="production"
    eb init $APP_NAME -p python-3.9 --region $AWS_REGION
    
    # Create/deploy the application
    echo "Creating Elastic Beanstalk environment and deploying application..."
    eb create $ENV_NAME
    
    # Get the application URL
    BACKEND_URL=$(eb status $ENV_NAME | grep CNAME | awk '{print $2}')
    
elif [ "$DEPLOYMENT_TYPE" = "ecs" ]; then
    # ECS Deployment
    
    # Create ECR repository if it doesn't exist
    REPO_NAME="s4-service"
    if ! aws ecr describe-repositories --repository-names $REPO_NAME 2>&1 > /dev/null; then
        echo "Creating ECR repository..."
        aws ecr create-repository --repository-name $REPO_NAME
    fi
    
    # Get repository URI
    REPO_URI=$(aws ecr describe-repositories --repository-names $REPO_NAME --query 'repositories[0].repositoryUri' --output text)
    
    # Build Docker image
    echo "Building S4 Docker image..."
    docker build -t s4-service:latest .
    
    # Tag and push to ECR
    echo "Tagging and pushing image to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REPO_URI
    docker tag s4-service:latest $REPO_URI:latest
    docker push $REPO_URI:latest
    
    # Create ECS task definition
    echo "Creating ECS task definition..."
    cat > task-definition.json << EOL
{
    "family": "s4-task",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "networkMode": "awsvpc",
    "containerDefinitions": [
        {
            "name": "s4-container",
            "image": "$REPO_URI:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8080,
                    "hostPort": 8080,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "S4_S3_BUCKET", "value": "$S4_S3_BUCKET"},
                {"name": "S4_S3_REGION", "value": "$AWS_REGION"},
                {"name": "OPENAI_API_KEY", "value": "$OPENAI_API_KEY"},
                {"name": "S4_ADMIN_API_KEY", "value": "$S4_ADMIN_API_KEY"},
                {"name": "S4_API_HOST", "value": "0.0.0.0"},
                {"name": "S4_API_PORT", "value": "8080"},
                {"name": "S4_CORS_ORIGINS", "value": "*"},
                {"name": "S4_DEBUG", "value": "false"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/s4-service",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ],
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048"
}
EOL

    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json
    
    # Create log group
    aws logs create-log-group --log-group-name "/ecs/s4-service" || true
    
    # Create ECS cluster if it doesn't exist
    CLUSTER_NAME="s4-cluster"
    if ! aws ecs describe-clusters --clusters $CLUSTER_NAME --query "clusters[0].clusterArn" --output text 2>&1 > /dev/null; then
        echo "Creating ECS cluster..."
        aws ecs create-cluster --cluster-name $CLUSTER_NAME
    fi
    
    # Create security group for ECS tasks
    echo "Creating security group for ECS tasks..."
    VPC_ID=$(aws ec2 describe-vpcs --query "Vpcs[0].VpcId" --output text)
    SG_NAME="s4-service-sg"
    
    SG_ID=$(aws ec2 create-security-group --group-name $SG_NAME --description "S4 Service Security Group" --vpc-id $VPC_ID --output text)
    
    # Allow inbound traffic on port 8080
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8080 --cidr 0.0.0.0/0
    
    # Create load balancer
    echo "Creating load balancer..."
    # Find public subnets in the VPC
    SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" --query "Subnets[*].SubnetId" --output text)
    SUBNET_IDS=($SUBNETS)
    
    LB_NAME="s4-lb"
    aws elbv2 create-load-balancer --name $LB_NAME --subnets ${SUBNET_IDS[@]} --security-groups $SG_ID
    
    LB_ARN=$(aws elbv2 describe-load-balancers --names $LB_NAME --query "LoadBalancers[0].LoadBalancerArn" --output text)
    
    # Create target group
    TG_NAME="s4-targets"
    aws elbv2 create-target-group --name $TG_NAME --protocol HTTP --port 8080 --vpc-id $VPC_ID --target-type ip --health-check-path "/health" --health-check-interval-seconds 30
    
    TG_ARN=$(aws elbv2 describe-target-groups --names $TG_NAME --query "TargetGroups[0].TargetGroupArn" --output text)
    
    # Create listener
    aws elbv2 create-listener --load-balancer-arn $LB_ARN --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$TG_ARN
    
    # Create ECS service
    echo "Creating ECS service..."
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name s4-service \
        --task-definition s4-task \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS[0]}],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
        --load-balancers "targetGroupArn=$TG_ARN,containerName=s4-container,containerPort=8080"
    
    # Get the load balancer URL
    BACKEND_URL=$(aws elbv2 describe-load-balancers --load-balancer-arns $LB_ARN --query "LoadBalancers[0].DNSName" --output text)
fi

echo -e "${GREEN}S4 backend deployed at: http://$BACKEND_URL${NC}"

# ===== FRONTEND DEPLOYMENT =====
echo ""
echo -e "${BLUE}Starting S4 UI deployment...${NC}"

# Navigate to the UI directory
cd s4-ui

# Create .env file with correct API URL
echo "Creating production .env file..."
echo "REACT_APP_API_URL=http://$BACKEND_URL/api" > .env.production
echo "Created .env.production file with API URL: http://$BACKEND_URL/api"

# Install dependencies and build
echo "Installing UI dependencies..."
npm install

echo "Building UI application..."
npm run build

# Create S3 bucket for UI hosting if it doesn't exist
echo "Checking S3 bucket for UI hosting..."
if ! aws s3 ls "s3://$UI_BUCKET_NAME" 2>&1 > /dev/null; then
    echo "Creating S3 bucket for UI hosting: $UI_BUCKET_NAME"
    aws s3 mb "s3://$UI_BUCKET_NAME" --region $AWS_REGION
    
    # Enable static website hosting
    aws s3 website "s3://$UI_BUCKET_NAME" --index-document index.html --error-document index.html
    
    # Create bucket policy to allow public access
    POLICY="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"PublicReadGetObject\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$UI_BUCKET_NAME/*\"}]}"
    aws s3api put-bucket-policy --bucket "$UI_BUCKET_NAME" --policy "$POLICY"
fi

# Upload the build folder
echo "Uploading UI files to S3..."
aws s3 sync build/ "s3://$UI_BUCKET_NAME" --delete

# Get the website URL
UI_URL="http://$UI_BUCKET_NAME.s3-website.$AWS_REGION.amazonaws.com"

# Add CloudFront distribution for better performance (optional)
echo "Would you like to set up a CloudFront distribution for the UI?"
echo "This will provide better performance and HTTPS support."
read -p "Set up CloudFront? (y/n): " SETUP_CLOUDFRONT

if [[ "$SETUP_CLOUDFRONT" =~ ^[Yy]$ ]]; then
    # Create CloudFront distribution
    echo "Creating CloudFront distribution..."
    
    # Create CloudFront origin access identity
    OAI_NAME="S4-UI-OAI"
    OAI_RESP=$(aws cloudfront create-cloud-front-origin-access-identity --cloud-front-origin-access-identity-config "CallerReference=$OAI_NAME,Comment=OAI for S4 UI")
    OAI_ID=$(echo $OAI_RESP | jq -r '.CloudFrontOriginAccessIdentity.Id')
    
    # Update bucket policy for CloudFront
    CLOUDFRONT_POLICY="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"2\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $OAI_ID\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$UI_BUCKET_NAME/*\"}]}"
    aws s3api put-bucket-policy --bucket "$UI_BUCKET_NAME" --policy "$CLOUDFRONT_POLICY"
    
    # Create CloudFront distribution
    DISTRIBUTION_CONFIG=$(cat <<EOF
{
  "CallerReference": "$(date +%s)",
  "Aliases": {
    "Quantity": 0
  },
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-$UI_BUCKET_NAME",
        "DomainName": "$UI_BUCKET_NAME.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/$OAI_ID"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-$UI_BUCKET_NAME",
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ViewerProtocolPolicy": "redirect-to-https",
    "MinTTL": 0,
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "SmoothStreaming": false,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "Compress": true
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  },
  "Comment": "S4 UI Distribution",
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
EOF
)
    
    # Create the distribution
    DISTRIBUTION_RESULT=$(aws cloudfront create-distribution --distribution-config "$DISTRIBUTION_CONFIG")
    
    # Extract the CloudFront domain name
    CF_DOMAIN=$(echo $DISTRIBUTION_RESULT | jq -r '.Distribution.DomainName')
    
    echo -e "${GREEN}CloudFront distribution created!${NC}"
    echo "Your UI will be available at: https://$CF_DOMAIN"
    echo "Note: It might take up to 15 minutes for the distribution to deploy."
    
    UI_URL="https://$CF_DOMAIN"
else
    echo -e "${YELLOW}Skipping CloudFront setup. Using S3 website URL.${NC}"
fi

# ===== FINALIZATION =====
echo ""
echo -e "${BLUE}===== Deployment Complete =====${NC}"
echo "S4 backend is available at: http://$BACKEND_URL"
echo "S4 UI is available at: $UI_URL"
echo "Admin API key: $S4_ADMIN_API_KEY"
echo ""
echo "To create your first tenant, use:"
echo "curl -X POST http://$BACKEND_URL/api/admin/tenants \\"
echo "  -H \"X-Admin-Key: $S4_ADMIN_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
echo ""
echo -e "${GREEN}Remember to save the tenant key from the response to use with the UI!${NC}"
echo ""
echo "=== Important Notes ==="
echo "1. The S3 bucket configuration uses public access for UI hosting. For production,"
echo "   consider adding CloudFront with HTTPS."
echo "2. This deployment doesn't include domain configuration. You'll need to add your"
echo "   own domain and SSL certificates for production use."
echo "3. Save the Admin API key in a secure location. It won't be displayed again." 