#!/bin/bash
# Script to set up Elastic Beanstalk deployment environment for S4

set -e  # Exit on error

echo "Setting up Elastic Beanstalk deployment for S4..."

# Check if awsebcli is installed
if ! command -v eb &> /dev/null; then
    echo "Installing AWS EB CLI..."
    pip install awsebcli
fi

# Create .ebextensions directory if it doesn't exist
if [ ! -d ".ebextensions" ]; then
    echo "Creating .ebextensions directory..."
    mkdir -p .ebextensions
fi

# Create the EB configuration file
echo "Creating Elastic Beanstalk configuration file..."
cat > .ebextensions/01_s4.config << 'EOL'
option_settings:
  aws:elasticbeanstalk:application:environment:
    AWS_ACCESS_KEY_ID: REPLACE_WITH_YOUR_KEY
    AWS_SECRET_ACCESS_KEY: REPLACE_WITH_YOUR_SECRET
    S4_S3_BUCKET: your-s4-bucket
    S4_S3_REGION: us-east-1
    OPENAI_API_KEY: REPLACE_WITH_YOUR_KEY
    S4_DISABLE_API_AUTH: false
    S4_ADMIN_API_KEY: REPLACE_WITH_YOUR_SECURE_KEY
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
cat > Procfile << 'EOL'
web: python -m s4 start --host=0.0.0.0 --port=8080
EOL

# Create .ebignore file to control what gets deployed
echo "Creating .ebignore file..."
cat > .ebignore << 'EOL'
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

# Only necessary for local development
deploy.sh
setup_eb.sh
EOL

# Reminder to initialize EB
echo "Setup complete! You can now initialize Elastic Beanstalk with:"
echo "  eb init -p python-3.9 s4-service"
echo ""
echo "Then deploy with:"
echo "  eb create s4-production"
echo ""
echo "IMPORTANT: Before deploying, edit .ebextensions/01_s4.config to set your actual credentials and configuration." 