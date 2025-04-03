#!/bin/bash
set -e

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with required environment variables."
    exit 1
fi

# Build and start docker containers
echo "Starting S4 service with docker-compose..."
docker-compose up -d --build

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Check if service is running
if docker-compose ps | grep -q "s4"; then
    echo "S4 service is running!"
    echo "API is available at: http://localhost:8000"
    echo "API documentation is available at: http://localhost:8000/docs"
    echo "Admin API documentation is available at: http://localhost:8000/docs#/admin"
    
    # Get admin API key from .env file
    ADMIN_KEY=$(grep S4_ADMIN_API_KEY .env | cut -d '=' -f2)
    
    echo ""
    echo "Use the following Admin API key for tenant management:"
    echo "Admin API Key: $ADMIN_KEY"
    echo ""
    echo "To create your first tenant, use:"
    echo "curl -X POST http://localhost:8000/api/admin/tenants \\"
    echo "  -H \"X-Admin-Key: $ADMIN_KEY\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
else
    echo "Error: S4 service failed to start. Check logs with 'docker-compose logs'"
    exit 1
fi 