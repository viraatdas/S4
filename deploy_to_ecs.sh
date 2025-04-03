#!/bin/bash
# S4 Deployment Script for AWS ECS
set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== S4 AWS ECS Deployment Script =====${NC}"
echo -e "This script will deploy S4 to AWS ECS"
echo ""

# Check AWS CLI installation
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html for installation instructions."
    exit 1
fi

# Check if aws credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured or invalid.${NC}"
    echo "Please run 'aws configure' to set up your credentials."
    exit 1
fi

# Get AWS account details
echo "Verifying AWS credentials..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    echo -e "${YELLOW}AWS region not configured.${NC}"
    read -p "Enter AWS region (e.g., us-east-1): " AWS_REGION
    aws configure set region $AWS_REGION
fi

echo -e "${GREEN}Using AWS Account: $AWS_ACCOUNT_ID in region: $AWS_REGION${NC}"

# Configuration
S4_S3_BUCKET=""
OPENAI_API_KEY=""
S4_ADMIN_API_KEY=""
CLUSTER_NAME="s4-cluster"
SERVICE_NAME="s4-service"
UI_SERVICE_NAME="s4-ui"
BACKEND_ECR_REPO="s4-backend"
UI_ECR_REPO="s4-ui"
BACKEND_CONTAINER_NAME="s4-backend"
UI_CONTAINER_NAME="s4-ui"
LB_NAME="s4-alb"

# Prompt for required information
read -p "Enter S3 bucket name for S4 storage (lowercase, no spaces): " S4_S3_BUCKET
read -p "Enter OpenAI API key: " OPENAI_API_KEY

# Generate admin key if not provided
read -p "Enter secure admin API key (or press enter to generate one): " S4_ADMIN_API_KEY
if [ -z "$S4_ADMIN_API_KEY" ]; then
    S4_ADMIN_API_KEY=$(openssl rand -hex 16)
    echo "Generated Admin API Key: $S4_ADMIN_API_KEY"
    echo "IMPORTANT: Save this key securely!"
fi

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

# Create ECR repositories
echo "Creating ECR repositories..."
if ! aws ecr describe-repositories --repository-names $BACKEND_ECR_REPO 2>&1 > /dev/null; then
    echo "Creating ECR repository for backend: $BACKEND_ECR_REPO"
    aws ecr create-repository --repository-name $BACKEND_ECR_REPO
fi

if ! aws ecr describe-repositories --repository-names $UI_ECR_REPO 2>&1 > /dev/null; then
    echo "Creating ECR repository for UI: $UI_ECR_REPO"
    aws ecr create-repository --repository-name $UI_ECR_REPO
fi

# Get repository URIs
BACKEND_REPO_URI=$(aws ecr describe-repositories --repository-names $BACKEND_ECR_REPO --query 'repositories[0].repositoryUri' --output text)
UI_REPO_URI=$(aws ecr describe-repositories --repository-names $UI_ECR_REPO --query 'repositories[0].repositoryUri' --output text)

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $BACKEND_REPO_URI

# Build and push Docker images
echo "Building and pushing backend image..."
docker build -t $BACKEND_ECR_REPO:latest .
docker tag $BACKEND_ECR_REPO:latest $BACKEND_REPO_URI:latest
docker push $BACKEND_REPO_URI:latest

# Create ECS cluster if it doesn't exist
echo "Creating ECS cluster..."
if ! aws ecs describe-clusters --clusters $CLUSTER_NAME --query "clusters[0].clusterName" --output text 2>&1 > /dev/null; then
    aws ecs create-cluster --cluster-name $CLUSTER_NAME
fi

# Create log groups
echo "Creating CloudWatch log groups..."
aws logs create-log-group --log-group-name "/ecs/$SERVICE_NAME" || true
aws logs create-log-group --log-group-name "/ecs/$UI_SERVICE_NAME" || true

# Get VPC and subnet information
echo "Getting VPC information..."
VPC_ID=$(aws ec2 describe-vpcs --query "Vpcs[0].VpcId" --output text)
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" --query "Subnets[*].SubnetId" --output text)
SUBNET_IDS=($SUBNETS)

if [ ${#SUBNET_IDS[@]} -lt 2 ]; then
    echo -e "${RED}Error: Need at least two public subnets for the load balancer.${NC}"
    exit 1
fi

# Create security groups
echo "Creating security groups..."
BACKEND_SG_NAME="s4-backend-sg"
UI_SG_NAME="s4-ui-sg"
ALB_SG_NAME="s4-alb-sg"

# Create ALB security group
ALB_SG_ID=$(aws ec2 create-security-group --group-name $ALB_SG_NAME --description "S4 Load Balancer Security Group" --vpc-id $VPC_ID --output text)
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0

# Create backend security group
BACKEND_SG_ID=$(aws ec2 create-security-group --group-name $BACKEND_SG_NAME --description "S4 Backend Security Group" --vpc-id $VPC_ID --output text)
aws ec2 authorize-security-group-ingress --group-id $BACKEND_SG_ID --protocol tcp --port 8000 --source-group $ALB_SG_ID

# Create UI security group
UI_SG_ID=$(aws ec2 create-security-group --group-name $UI_SG_NAME --description "S4 UI Security Group" --vpc-id $VPC_ID --output text)
aws ec2 authorize-security-group-ingress --group-id $UI_SG_ID --protocol tcp --port 80 --source-group $ALB_SG_ID

# Create Application Load Balancer
echo "Creating Application Load Balancer..."
aws elbv2 create-load-balancer --name $LB_NAME --subnets ${SUBNET_IDS[@]} --security-groups $ALB_SG_ID --type application

# Wait for the load balancer to be created
echo "Waiting for load balancer to be created..."
sleep 30

# Get load balancer ARN
LB_ARN=$(aws elbv2 describe-load-balancers --names $LB_NAME --query "LoadBalancers[0].LoadBalancerArn" --output text)
LB_DNS=$(aws elbv2 describe-load-balancers --names $LB_NAME --query "LoadBalancers[0].DNSName" --output text)

echo "Building and pushing UI image..."
cd s4-ui

# Create .env.production for the UI build with the correct API URL
echo "REACT_APP_API_URL=http://$LB_DNS/api" > .env.production
echo "Created .env.production with API URL: http://$LB_DNS/api"

docker build -t $UI_ECR_REPO:latest .
docker tag $UI_ECR_REPO:latest $UI_REPO_URI:latest
docker push $UI_REPO_URI:latest

cd ..

# Create target groups
echo "Creating target groups..."
BACKEND_TG_NAME="s4-backend-tg"
UI_TG_NAME="s4-ui-tg"

aws elbv2 create-target-group --name $BACKEND_TG_NAME --protocol HTTP --port 8000 --vpc-id $VPC_ID --target-type ip --health-check-path "/health" --health-check-interval-seconds 30
aws elbv2 create-target-group --name $UI_TG_NAME --protocol HTTP --port 80 --vpc-id $VPC_ID --target-type ip --health-check-path "/" --health-check-interval-seconds 30

BACKEND_TG_ARN=$(aws elbv2 describe-target-groups --names $BACKEND_TG_NAME --query "TargetGroups[0].TargetGroupArn" --output text)
UI_TG_ARN=$(aws elbv2 describe-target-groups --names $UI_TG_NAME --query "TargetGroups[0].TargetGroupArn" --output text)

# Create listeners
echo "Creating listeners..."
UI_LISTENER_ARN=$(aws elbv2 create-listener --load-balancer-arn $LB_ARN --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$UI_TG_ARN --query "Listeners[0].ListenerArn" --output text)

# Create listener rule for API
aws elbv2 create-rule --listener-arn $UI_LISTENER_ARN --priority 10 --conditions Field=path-pattern,Values='/api/*' --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN

# Create IAM role for ECS task execution
echo "Creating IAM roles..."
EXECUTION_ROLE_NAME="ecsTaskExecutionRole"

# Check if role exists
if ! aws iam get-role --role-name $EXECUTION_ROLE_NAME &>/dev/null; then
    aws iam create-role --role-name $EXECUTION_ROLE_NAME --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'
    aws iam attach-role-policy --role-name $EXECUTION_ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    aws iam attach-role-policy --role-name $EXECUTION_ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
fi

# Create task definitions
echo "Creating task definitions..."

# Backend task definition
cat > backend-task-def.json << EOL
{
    "family": "s4-backend",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/$EXECUTION_ROLE_NAME",
    "networkMode": "awsvpc",
    "containerDefinitions": [
        {
            "name": "$BACKEND_CONTAINER_NAME",
            "image": "$BACKEND_REPO_URI:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "hostPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "S4_S3_BUCKET", "value": "$S4_S3_BUCKET"},
                {"name": "S4_S3_REGION", "value": "$AWS_REGION"},
                {"name": "OPENAI_API_KEY", "value": "$OPENAI_API_KEY"},
                {"name": "S4_ADMIN_API_KEY", "value": "$S4_ADMIN_API_KEY"},
                {"name": "S4_API_HOST", "value": "0.0.0.0"},
                {"name": "S4_API_PORT", "value": "8000"},
                {"name": "S4_CORS_ORIGINS", "value": "*"},
                {"name": "S4_DEBUG", "value": "false"},
                {"name": "S4_DATA_DIR", "value": "/app/data"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$SERVICE_NAME",
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

# UI task definition
cat > ui-task-def.json << EOL
{
    "family": "s4-ui",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/$EXECUTION_ROLE_NAME",
    "networkMode": "awsvpc",
    "containerDefinitions": [
        {
            "name": "$UI_CONTAINER_NAME",
            "image": "$UI_REPO_URI:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 80,
                    "hostPort": 80,
                    "protocol": "tcp"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$UI_SERVICE_NAME",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ],
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024"
}
EOL

# Register task definitions
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
aws ecs register-task-definition --cli-input-json file://ui-task-def.json

# Create ECS services
echo "Creating ECS services..."

# Backend service
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition s4-backend \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS[0]}],securityGroups=[$BACKEND_SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=$BACKEND_CONTAINER_NAME,containerPort=8000"

# UI service
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $UI_SERVICE_NAME \
    --task-definition s4-ui \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS[0]}],securityGroups=[$UI_SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$UI_TG_ARN,containerName=$UI_CONTAINER_NAME,containerPort=80"

# Finalization
echo -e "${GREEN}S4 deployment to AWS ECS complete!${NC}"
echo "Load Balancer URL: http://$LB_DNS"
echo "API URL: http://$LB_DNS/api"
echo "Admin API Key: $S4_ADMIN_API_KEY"
echo ""
echo "To create your first tenant, use:"
echo "curl -X POST http://$LB_DNS/api/admin/tenants \\"
echo "  -H \"X-Admin-Key: $S4_ADMIN_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
echo ""
echo -e "${YELLOW}Important Notes:${NC}"
echo "1. It may take a few minutes for the services to start up."
echo "2. For a production environment, consider setting up HTTPS with AWS Certificate Manager."
echo "3. To add a custom domain, configure Route 53 and update the load balancer." 