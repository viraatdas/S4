#!/bin/bash
# S4 Deployment Script for Docker Compose
set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== S4 Docker Compose Deployment Script =====${NC}"
echo -e "This script will deploy S4 locally using Docker Compose"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not found. Please install it first:${NC}"
    echo "https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose not found. Please install it first:${NC}"
    echo "https://docs.docker.com/compose/install/"
    exit 1
fi

# Collect required information
S4_S3_BUCKET=""
OPENAI_API_KEY=""
S4_ADMIN_API_KEY=""

read -p "Enter S3 bucket name for S4 storage (lowercase, no spaces): " S4_S3_BUCKET
read -p "Enter AWS region for S3 bucket: " S4_S3_REGION
read -p "Enter OpenAI API key: " OPENAI_API_KEY

# Generate admin key if not provided
read -p "Enter secure admin API key (or press enter to generate one): " S4_ADMIN_API_KEY
if [ -z "$S4_ADMIN_API_KEY" ]; then
    S4_ADMIN_API_KEY=$(openssl rand -hex 16)
    echo "Generated Admin API Key: $S4_ADMIN_API_KEY"
    echo "IMPORTANT: Save this key securely!"
fi

# Check AWS credentials
echo "Testing AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${YELLOW}Warning: AWS credentials not found or invalid.${NC}"
    echo "Please make sure your AWS credentials are configured correctly:"
    echo "- ~/.aws/credentials file with valid access key and secret"
    echo "- Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
    
    # Ask for AWS credentials
    read -p "Would you like to enter AWS credentials now? (y/n): " ENTER_CREDS
    if [[ $ENTER_CREDS == "y" ]]; then
        read -p "Enter AWS Access Key ID: " AWS_ACCESS_KEY_ID
        read -p "Enter AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
        
        # Export for use in Docker
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
    else
        echo "Proceeding without AWS credentials. S3 storage may not work correctly."
    fi
fi

# Create .env file
echo "Creating .env file..."
cat > .env << EOL
# AWS Credentials
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# S3 Configuration
S4_S3_BUCKET=${S4_S3_BUCKET}
S4_S3_REGION=${S4_S3_REGION}

# OpenAI API Key
OPENAI_API_KEY=${OPENAI_API_KEY}

# Multi-tenant settings
S4_DISABLE_API_AUTH=false
S4_ADMIN_API_KEY=${S4_ADMIN_API_KEY}

# API settings
S4_API_HOST=0.0.0.0
S4_API_PORT=8000
S4_CORS_ORIGINS=*

# Optional settings
S4_DEBUG=true
S4_DATA_DIR=/app/data
S4_EMBEDDING_MODEL=text-embedding-3-small
EOL

# Create .env file for frontend
echo "Creating .env file for frontend..."
mkdir -p s4-ui
cat > s4-ui/.env << EOL
REACT_APP_API_URL=http://localhost:8000/api
EOL

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Creating docker-compose.yml..."
    cat > docker-compose.yml << EOL
version: '3.8'

services:
  s4:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  s4-ui:
    build: ./s4-ui
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
    depends_on:
      - s4
    restart: unless-stopped
EOL
fi

# Build and start containers
echo -e "${BLUE}Building and starting S4 containers...${NC}"
docker-compose build
docker-compose up -d

# Wait for containers to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "s4.*Up"; then
    echo -e "${GREEN}S4 backend is running!${NC}"
else
    echo -e "${RED}S4 backend failed to start. Check logs with 'docker-compose logs s4'${NC}"
    exit 1
fi

if docker-compose ps | grep -q "s4-ui.*Up"; then
    echo -e "${GREEN}S4 frontend is running!${NC}"
else
    echo -e "${RED}S4 frontend failed to start. Check logs with 'docker-compose logs s4-ui'${NC}"
    exit 1
fi

# Get container IP
BACKEND_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker-compose ps -q s4))

# Finalization
echo -e "${GREEN}===== Deployment Complete =====${NC}"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost"
echo "Admin API key: $S4_ADMIN_API_KEY"
echo ""
echo "To create your first tenant, use:"
echo "curl -X POST http://localhost:8000/api/admin/tenants \\"
echo "  -H \"X-Admin-Key: $S4_ADMIN_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Create a tenant using the command above"
echo "2. Use the returned tenant key to log in to the frontend UI"
echo ""
echo -e "${YELLOW}Admin Portal Access:${NC}"
echo "1. Access the Admin Portal at: http://localhost/admin/login"
echo "2. Log in using your Admin API key: $S4_ADMIN_API_KEY"
echo "3. You can manage tenants, subscriptions, and view system data directly through the UI"
echo ""
echo -e "${GREEN}Thank you for deploying S4!${NC}" 