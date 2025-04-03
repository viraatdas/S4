#!/bin/bash

# Clean up the repository by removing unwanted files
echo "Cleaning up repository..."

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

# Remove Node.js modules
rm -rf s4-ui/node_modules
rm -rf node_modules

# Remove build directories
rm -rf s4-ui/build
rm -rf build
rm -rf dist
rm -rf *.egg-info

# Remove deployment artifacts
rm -rf amplify-deploy
rm -rf *.zip

# Remove any remaining sensitive files
rm -f ~/.aws/credentials

echo "Repository cleaned successfully!"
