#!/bin/bash
# S4 Run Script
# This script helps you run, stop, and manage your S4 application

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function show_help {
  echo -e "${BLUE}S4 Management Script${NC}"
  echo ""
  echo "Usage: ./run.sh [command]"
  echo ""
  echo "Commands:"
  echo "  start       - Start the S4 backend and UI"
  echo "  stop        - Stop the running containers"
  echo "  restart     - Restart the S4 services"
  echo "  status      - Check the status of the S4 services"
  echo "  logs        - View the logs of the S4 services"
  echo "  setup       - Configure the .env file"
  echo "  create-tenant - Create a new tenant"
  echo "  help        - Show this help"
  echo ""
}

function check_dependencies {
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
  fi

  if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
  fi
}

function setup_env {
  echo -e "${BLUE}Setting up S4 environment...${NC}"
  
  if [ -f .env ]; then
    echo -e "${YELLOW}A .env file already exists.${NC}"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
      echo "Keeping existing .env file."
      return
    fi
  fi
  
  echo "Please provide the following configuration values:"
  
  # Get OpenAI API Key
  read -p "OpenAI API Key (required for embeddings): " openai_key
  
  # Generate admin key if not provided
  read -p "Admin API Key (or press enter to generate one): " admin_key
  if [ -z "$admin_key" ]; then
    admin_key=$(openssl rand -hex 16)
    echo "Generated Admin API Key: $admin_key"
    echo "IMPORTANT: Save this key securely!"
  fi
  
  # Ask for S3 configuration
  read -p "Use S3 for storage? (y/n, default: n): " use_s3
  if [[ "$use_s3" =~ ^[Yy]$ ]]; then
    read -p "S3 Bucket Name: " s3_bucket
    read -p "S3 Region (default: us-east-1): " s3_region
    s3_region=${s3_region:-us-east-1}
    read -p "AWS Access Key ID: " aws_access_key
    read -p "AWS Secret Access Key: " aws_secret_key
  fi
  
  # Create the .env file
  cat > .env << EOL
# S4 Environment Configuration
# ===========================

# OpenAI API Key - Required for embeddings and semantic search
OPENAI_API_KEY=${openai_key}

# Admin API Key - Used to access the admin API
S4_ADMIN_API_KEY=${admin_key}

# API Configuration
S4_API_HOST=0.0.0.0
S4_API_PORT=8000
S4_CORS_ORIGINS=*
S4_DEBUG=false
S4_DATA_DIR=/app/data

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api
EOL

  # Add S3 configuration if selected
  if [[ "$use_s3" =~ ^[Yy]$ ]]; then
    cat >> .env << EOL

# S3 Configuration
S4_S3_BUCKET=${s3_bucket}
S4_S3_REGION=${s3_region}
AWS_ACCESS_KEY_ID=${aws_access_key}
AWS_SECRET_ACCESS_KEY=${aws_secret_key}
EOL
  fi
  
  echo -e "${GREEN}Environment configuration complete!${NC}"
}

function start_services {
  echo -e "${BLUE}Starting S4 services...${NC}"
  docker-compose up -d
  
  echo ""
  echo -e "${GREEN}S4 services started!${NC}"
  echo "Backend API: http://localhost:8000"
  echo "Frontend UI: http://localhost:80"
  echo "API Documentation: http://localhost:8000/docs"
}

function stop_services {
  echo -e "${BLUE}Stopping S4 services...${NC}"
  docker-compose down
  echo -e "${GREEN}S4 services stopped.${NC}"
}

function restart_services {
  echo -e "${BLUE}Restarting S4 services...${NC}"
  docker-compose restart
  echo -e "${GREEN}S4 services restarted.${NC}"
}

function show_status {
  echo -e "${BLUE}S4 Services Status:${NC}"
  docker-compose ps
}

function show_logs {
  echo -e "${BLUE}S4 Services Logs:${NC}"
  docker-compose logs -f
}

function create_tenant {
  if [ ! -f .env ]; then
    echo -e "${RED}Error: No .env file found. Run './run.sh setup' first.${NC}"
    exit 1
  fi
  
  source .env
  
  if [ -z "$S4_ADMIN_API_KEY" ]; then
    echo -e "${RED}Error: No admin API key found in .env file.${NC}"
    exit 1
  fi
  
  # Get tenant information
  echo -e "${BLUE}Creating a new tenant...${NC}"
  read -p "Tenant Name: " tenant_name
  read -p "Tenant Email: " tenant_email
  read -p "Company Name: " company_name
  read -p "Plan ID (default: basic): " plan_id
  plan_id=${plan_id:-basic}
  
  # Make the API call to create a tenant
  echo "Creating tenant..."
  tenant_response=$(curl -s -X POST http://localhost:8000/api/admin/tenants \
    -H "X-Admin-Key: $S4_ADMIN_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$tenant_name\", \"email\": \"$tenant_email\", \"company\": \"$company_name\", \"plan_id\": \"$plan_id\"}")
  
  tenant_key=$(echo $tenant_response | grep -o '"tenant_key":"[^"]*' | sed 's/"tenant_key":"//')
  
  if [ -n "$tenant_key" ]; then
    echo -e "${GREEN}Tenant created successfully!${NC}"
    echo "Tenant Key: $tenant_key"
    echo "IMPORTANT: Save this tenant key to access the API."
    echo ""
    echo "Use this tenant key when logging into the UI."
  else
    echo -e "${RED}Failed to create tenant. Response:${NC}"
    echo $tenant_response
  fi
}

# Check dependencies
check_dependencies

# Process commands
if [ "$#" -eq 0 ]; then
  show_help
  exit 0
fi

case "$1" in
  start)
    start_services
    ;;
  stop)
    stop_services
    ;;
  restart)
    restart_services
    ;;
  status)
    show_status
    ;;
  logs)
    show_logs
    ;;
  setup)
    setup_env
    ;;
  create-tenant)
    create_tenant
    ;;
  help)
    show_help
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}"
    show_help
    exit 1
    ;;
esac 