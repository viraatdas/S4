#!/bin/bash
# Script to set up Google Cloud Run deployment for S4

set -e  # Exit on error

echo "Setting up Google Cloud Run deployment for S4..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: Google Cloud SDK (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

# Check if project exists
echo "Verifying project..."
if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    echo "Error: Project $PROJECT_ID not found or you don't have access."
    exit 1
fi

# Set project
gcloud config set project "$PROJECT_ID"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Docker is required for building the container image."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create an Artifact Registry repository
REPO_NAME="s4-repo"
REGION="us-central1"  # Default region
read -p "Enter the region for deployment [default: $REGION]: " INPUT_REGION
REGION=${INPUT_REGION:-$REGION}

echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Repository for S4 Service"

# Create a .env.gcloud file for reference
echo "Creating reference .env.gcloud file..."
cat > .env.gcloud << 'EOL'
# Reference environment variables for Google Cloud Run deployment
# These will be passed as environment variables to the Cloud Run service
AWS_ACCESS_KEY_ID=REPLACE_WITH_YOUR_KEY
AWS_SECRET_ACCESS_KEY=REPLACE_WITH_YOUR_SECRET
S4_S3_BUCKET=your-s4-bucket
S4_S3_REGION=us-east-1
OPENAI_API_KEY=REPLACE_WITH_YOUR_KEY
S4_DISABLE_API_AUTH=false
S4_ADMIN_API_KEY=REPLACE_WITH_YOUR_SECURE_KEY
S4_API_HOST=0.0.0.0
S4_API_PORT=8080
S4_CORS_ORIGINS=*
S4_DEBUG=false
S4_DATA_DIR=/tmp
EOL

# Create deployment script
echo "Creating Cloud Run deployment script..."
cat > deploy_gcloud.sh << EOL
#!/bin/bash
# Script to deploy S4 to Google Cloud Run

set -e  # Exit on error

PROJECT_ID="$PROJECT_ID"
REGION="$REGION"
REPO_NAME="$REPO_NAME"
SERVICE_NAME="s4-service"

# Build and push the Docker image
echo "Building and pushing Docker image..."
IMAGE_URL="\${REGION}-docker.pkg.dev/\${PROJECT_ID}/\${REPO_NAME}/\${SERVICE_NAME}:latest"

# Authenticate Docker to Artifact Registry
gcloud auth configure-docker \${REGION}-docker.pkg.dev

# Build and push
docker build -t "\${IMAGE_URL}" .
docker push "\${IMAGE_URL}"

# Load environment variables from .env.gcloud
ENV_VARS=""
while IFS='=' read -r key value || [[ -n "\$key" ]]; do
    # Skip comments and empty lines
    [[ "\$key" =~ ^#.*$ ]] && continue
    [[ -z "\$key" ]] && continue
    
    # Add to ENV_VARS string
    ENV_VARS="\${ENV_VARS},\${key}=\${value}"
done < .env.gcloud

# Remove leading comma
ENV_VARS=\${ENV_VARS:1}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "\${SERVICE_NAME}" \\
  --image="\${IMAGE_URL}" \\
  --platform=managed \\
  --region="\${REGION}" \\
  --allow-unauthenticated \\
  --memory=2Gi \\
  --cpu=1 \\
  --min-instances=0 \\
  --max-instances=10 \\
  --set-env-vars="\${ENV_VARS}"

# Get the service URL
SERVICE_URL=\$(gcloud run services describe "\${SERVICE_NAME}" --platform=managed --region="\${REGION}" --format='value(status.url)')

echo ""
echo "Deployment complete! Your S4 service is available at: \${SERVICE_URL}"
echo ""
echo "API Documentation: \${SERVICE_URL}/docs"
echo ""
echo "To create a tenant, use:"
echo "curl -X POST \${SERVICE_URL}/api/admin/tenants \\"
echo "  -H \"X-Admin-Key: YOUR_ADMIN_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"name\": \"Example Company\", \"email\": \"admin@example.com\", \"company\": \"Example Inc\", \"plan_id\": \"basic\"}'"
EOL

# Make the deployment script executable
chmod +x deploy_gcloud.sh

echo ""
echo "Setup complete! Before deploying:"
echo "1. Edit .env.gcloud with your actual credentials and configuration"
echo "2. Run ./deploy_gcloud.sh to deploy to Google Cloud Run"
echo ""
echo "Note: The S4 data will be stored in the container's ephemeral filesystem (/tmp)."
echo "For production, consider setting up a more persistent storage solution." 