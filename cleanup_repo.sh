#!/bin/bash
# Script to clean up and organize the S4 repository

set -e

echo "S4 Repository Cleanup and Organization Tool"
echo "==========================================="
echo ""

# Make script executable
chmod +x deploy_unified.sh

# Create backup directory
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# 1. Consolidate deployment scripts
echo "Consolidating deployment scripts..."
cp deploy.sh "$BACKUP_DIR/"
cp deploy_amplify.sh "$BACKUP_DIR/"
cp deploy_amplify_auto.sh "$BACKUP_DIR/"
cp deploy_docker.sh "$BACKUP_DIR/"
cp deploy_docker_simple.sh "$BACKUP_DIR/"
cp deploy_frontend_only.sh "$BACKUP_DIR/"
cp deploy_to_eb.sh "$BACKUP_DIR/"
cp deploy_to_ecs.sh "$BACKUP_DIR/"

# Create a README file for the backup directory
cat > "$BACKUP_DIR/README.md" << EOF
# Backup of Original Deployment Scripts

This directory contains the original deployment scripts that were consolidated into \`deploy_unified.sh\`.

These files are kept for reference but are no longer needed for normal operation.
EOF

echo "Original deployment scripts backed up to $BACKUP_DIR"

# 2. Create utils directory if it doesn't exist
if [ ! -d "s4/utils" ]; then
    mkdir -p s4/utils
    touch s4/utils/__init__.py
    echo "Created utils directory and __init__.py file"
fi

# 3. Create documentation for the unified deployment script
cat > "DEPLOYMENT.md" << EOF
# S4 Deployment Guide

This guide explains how to deploy the S4 application using the unified deployment script.

## Prerequisites

- Ensure you have all required environment variables set (see \`env-unified-template.txt\`)
- Make sure you have the necessary AWS credentials if deploying to AWS services

## Deployment Options

The \`deploy_unified.sh\` script supports multiple deployment targets:

### Docker Deployment

For local development or simple deployments:

\`\`\`bash
./deploy_unified.sh --target docker
\`\`\`

### AWS Amplify Deployment

For deploying the frontend to AWS Amplify:

\`\`\`bash
./deploy_unified.sh --target amplify
\`\`\`

### Elastic Beanstalk Deployment

For deploying to AWS Elastic Beanstalk:

\`\`\`bash
./deploy_unified.sh --target eb
\`\`\`

### ECS Deployment

For deploying to AWS ECS:

\`\`\`bash
./deploy_unified.sh --target ecs
\`\`\`

## Additional Options

- \`--auto\`: Run in automatic mode without prompts
- \`--frontend-only\`: Deploy only the frontend
- \`--backend-only\`: Deploy only the backend
- \`--skip-build\`: Skip build step
- \`--skip-tests\`: Skip running tests
- \`--verbose\`: Verbose output
- \`--help\`: Show help message

## Environment Variables

See \`env-unified-template.txt\` for all required environment variables.
EOF

echo "Created DEPLOYMENT.md with documentation for the unified deployment script"

# 4. Create a script to help clean Git history of sensitive credentials
cat > "git_clean_credentials.sh" << 'EOF'
#!/bin/bash
# Script to clean sensitive credentials from Git history

set -e

echo "S4 Git History Credential Cleaner"
echo "================================="
echo ""
echo "WARNING: This script will rewrite Git history. Make sure you understand the implications."
echo "It's recommended to backup your repository before proceeding."
echo ""
echo "This script will help remove sensitive credentials that were previously hardcoded"
echo "in the repository, including:"
echo "- Google OAuth Client ID and Secret"
echo "- SuperTokens connection URI and API key"
echo "- OpenAI API Key"
echo ""
read -p "Do you want to continue? (y/n): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# Create a temporary file with patterns to search and replace
TMP_FILE=$(mktemp)

echo "Please enter the sensitive credentials to remove from Git history."
echo "Leave blank and press Enter if you don't want to replace a particular item."
echo ""

read -p "Google Client ID (e.g., 123456789-abcdef.apps.googleusercontent.com): " GOOGLE_CLIENT_ID
read -p "Google Client Secret (e.g., GOCSPX-abcdefg): " GOOGLE_CLIENT_SECRET
read -p "SuperTokens Connection URI (e.g., https://st-dev-xxxx.aws.supertokens.io): " SUPERTOKENS_URI
read -p "SuperTokens API Key: " SUPERTOKENS_API_KEY
read -p "OpenAI API Key (e.g., sk-xxxx): " OPENAI_API_KEY

# Build the filter-branch command with replacements
if [[ -n "$GOOGLE_CLIENT_ID" ]]; then
    echo "s/$GOOGLE_CLIENT_ID/YOUR_GOOGLE_CLIENT_ID/g" >> "$TMP_FILE"
fi

if [[ -n "$GOOGLE_CLIENT_SECRET" ]]; then
    echo "s/$GOOGLE_CLIENT_SECRET/YOUR_GOOGLE_CLIENT_SECRET/g" >> "$TMP_FILE"
fi

if [[ -n "$SUPERTOKENS_URI" ]]; then
    echo "s|$SUPERTOKENS_URI|YOUR_SUPERTOKENS_URI|g" >> "$TMP_FILE"
fi

if [[ -n "$SUPERTOKENS_API_KEY" ]]; then
    echo "s/$SUPERTOKENS_API_KEY/YOUR_SUPERTOKENS_API_KEY/g" >> "$TMP_FILE"
fi

if [[ -n "$OPENAI_API_KEY" ]]; then
    echo "s/$OPENAI_API_KEY/YOUR_OPENAI_API_KEY/g" >> "$TMP_FILE"
fi

if [[ ! -s "$TMP_FILE" ]]; then
    echo "No credentials provided. Exiting."
    rm "$TMP_FILE"
    exit 0
fi

echo ""
echo "The following files will be checked for credentials:"
echo "- s4-ui/src/config/supertokens.js"
echo "- simple_server.py"
echo "- test_auth.py"
echo "- s4-ui/src/pages/LoginPage.js"
echo "- s4-ui/src/pages/OAuthCallbackPage.js"
echo "- All deployment scripts"
echo ""

read -p "Do you want to proceed with cleaning the Git history? (y/n): " confirm_final

if [[ "$confirm_final" != "y" && "$confirm_final" != "Y" ]]; then
    echo "Operation cancelled."
    rm "$TMP_FILE"
    exit 0
fi

echo "Cleaning Git history. This may take a while..."

# Use git filter-branch to rewrite history
git filter-branch --force --tree-filter "
    if [ -f s4-ui/src/config/supertokens.js ]; then
        sed -i.bak -f $TMP_FILE s4-ui/src/config/supertokens.js
    fi
    if [ -f simple_server.py ]; then
        sed -i.bak -f $TMP_FILE simple_server.py
    fi
    if [ -f test_auth.py ]; then
        sed -i.bak -f $TMP_FILE test_auth.py
    fi
    if [ -f s4-ui/src/pages/LoginPage.js ]; then
        sed -i.bak -f $TMP_FILE s4-ui/src/pages/LoginPage.js
    fi
    if [ -f s4-ui/src/pages/OAuthCallbackPage.js ]; then
        sed -i.bak -f $TMP_FILE s4-ui/src/pages/OAuthCallbackPage.js
    fi
    find . -name '*.sh' -type f -exec sed -i.bak -f $TMP_FILE {} \;
    find . -name '*.bak' -type f -delete
" --tag-name-filter cat -- --all

# Clean up
rm "$TMP_FILE"

echo ""
echo "Git history has been rewritten to remove sensitive credentials."
echo ""
echo "IMPORTANT: You will need to force push these changes to your remote repository:"
echo "  git push origin --force --all"
echo "  git push origin --force --tags"
echo ""
echo "WARNING: This will overwrite the remote repository history. Make sure all collaborators"
echo "are aware of this change and pull the new history."
EOF

chmod +x git_clean_credentials.sh
echo "Created git_clean_credentials.sh to help clean sensitive credentials from Git history"

# 5. Create a README for the utils directory
cat > "s4/utils/README.md" << EOF
# S4 Utilities

This directory contains utility modules used throughout the S4 application.

## Modules

- **logging.py**: Unified logging configuration for consistent logging across the application
- **error_handling.py**: Error handling utilities including middleware for FastAPI

## Usage

Import these utilities as needed in your modules:

\`\`\`python
from s4.utils.logging import get_logger
from s4.utils.error_handling import format_error_response

logger = get_logger(__name__)

# Use logger
logger.info("This is an informational message")

# Use error handling
response = format_error_response(400, "Invalid input", {"field": "username"})
\`\`\`
EOF

echo "Created README.md for the utils directory"

# 6. Clean up unnecessary files
echo "Cleaning up unnecessary files..."

# Create a list of files to remove
cat > "files_to_remove.txt" << EOF
# This file contains a list of files that can be safely removed
# Remove the # at the beginning of the line to actually remove the file

# Redundant deployment scripts (now consolidated in deploy_unified.sh)
#deploy.sh
#deploy_amplify.sh
#deploy_amplify_auto.sh
#deploy_docker.sh
#deploy_docker_simple.sh
#deploy_frontend_only.sh
#deploy_to_eb.sh
#deploy_to_ecs.sh

# Redundant environment templates (now consolidated in .env.unified.example)
#.env.example
#env-template.txt
EOF

echo "Created files_to_remove.txt with suggestions for files to remove"

echo ""
echo "Cleanup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Review the unified deployment script (deploy_unified.sh)"
echo "2. Review the new documentation (DEPLOYMENT.md)"
echo "3. Consider running git_clean_credentials.sh to clean sensitive credentials from Git history"
echo "4. Review files_to_remove.txt and remove unnecessary files"
echo ""
echo "Note: Original deployment scripts have been backed up to $BACKUP_DIR"
