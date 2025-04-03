#!/bin/bash
set -e

echo "===== S4 Docker Compose Deployment Script (Simplified) ====="
echo "Deploying S4 locally using Docker Compose with preset values..."

# Hardcoded values
S3_BUCKET="s4-storage-prod"
AWS_REGION="us-east-1"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
ADMIN_API_KEY="s4_admin_key_123456"
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"

# Check for Docker and Docker Compose
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Error: Docker is not installed. Please install Docker first."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Error: Docker Compose is not installed. Please install Docker Compose first."; exit 1; }

# Create backend .env file
echo "Creating backend .env file..."
cat > .env << EOL
# AWS Configuration
AWS_ACCESS_KEY_ID=fake_access_key
AWS_SECRET_ACCESS_KEY=fake_secret_key
AWS_REGION=${AWS_REGION}

# S3 Configuration
S3_BUCKET=${S3_BUCKET}
UPLOAD_PATH=uploads

# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}

# Admin Configuration
ADMIN_API_KEY=${ADMIN_API_KEY}

# Service Configuration
DEBUG=True
ENVIRONMENT=development
PYTHONPATH=/app
EOL

# Create frontend .env file
echo "Creating frontend .env file..."
mkdir -p s4-ui
cat > s4-ui/.env << EOL
REACT_APP_API_URL=${BACKEND_URL}
REACT_APP_ENV=development
EOL

# Create docker-compose.yml if it doesn't exist
if [ ! -f "docker-compose.yml" ]; then
  echo "Creating docker-compose.yml file..."
  cat > docker-compose.yml << EOL
version: '3.8'

services:
  s4:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  s4-ui:
    build: ./s4-ui
    ports:
      - "3000:80"
    depends_on:
      - s4
    restart: unless-stopped
EOL
fi

# Build and start containers
echo "Building and starting Docker containers..."
docker compose up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking service status..."
if docker compose ps | grep -q "s4.*Up"; then
  echo "✅ Backend API is running."
else
  echo "❌ Backend API failed to start. Check logs with: docker compose logs s4"
fi

if docker compose ps | grep -q "s4-ui.*Up"; then
  echo "✅ Frontend UI is running."
else
  echo "❌ Frontend UI failed to start. Check logs with: docker compose logs s4-ui"
fi

# Output deployment information
echo ""
echo "===== Deployment Complete ====="
echo "Backend API: ${BACKEND_URL}"
echo "Frontend UI: ${FRONTEND_URL}"
echo "Admin API Key: ${ADMIN_API_KEY}"
echo ""
echo "To create your first tenant, run:"
echo "curl -X POST ${BACKEND_URL}/admin/tenants \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'X-API-Key: ${ADMIN_API_KEY}' \\"
echo "  -d '{\"name\": \"Test Tenant\", \"email\": \"test@example.com\", \"company\": \"Test Company\", \"plan_id\": \"basic\"}'"
echo ""
echo "Access the Admin Portal at: ${FRONTEND_URL}/admin/login"
echo "Log in using the Admin API Key."
echo ""
echo "Thank you for deploying S4!" 