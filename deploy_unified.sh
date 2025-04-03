#!/bin/bash
# Unified deployment script for S4
# Combines functionality from multiple deployment scripts

set -e

# Default values
DEPLOYMENT_TARGET="docker"
AUTO_MODE=false
FRONTEND_ONLY=false
BACKEND_ONLY=false
SKIP_BUILD=false
SKIP_TESTS=false
VERBOSE=false

# Display help information
show_help() {
    echo "Unified S4 Deployment Script"
    echo "Usage: ./deploy_unified.sh [options]"
    echo ""
    echo "Options:"
    echo "  -t, --target TARGET    Deployment target (docker, amplify, eb, ecs) [default: docker]"
    echo "  -a, --auto             Run in automatic mode without prompts"
    echo "  -f, --frontend-only    Deploy only the frontend"
    echo "  -b, --backend-only     Deploy only the backend"
    echo "  --skip-build           Skip build step"
    echo "  --skip-tests           Skip running tests"
    echo "  -v, --verbose          Verbose output"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy_unified.sh --target docker"
    echo "  ./deploy_unified.sh --target amplify --auto"
    echo "  ./deploy_unified.sh --frontend-only"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            DEPLOYMENT_TARGET="$2"
            shift 2
            ;;
        -a|--auto)
            AUTO_MODE=true
            shift
            ;;
        -f|--frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        -b|--backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate deployment target
if [[ ! "$DEPLOYMENT_TARGET" =~ ^(docker|amplify|eb|ecs)$ ]]; then
    echo "Error: Invalid deployment target '$DEPLOYMENT_TARGET'"
    echo "Valid targets are: docker, amplify, eb, ecs"
    exit 1
fi

# Validate conflicting options
if [ "$FRONTEND_ONLY" = true ] && [ "$BACKEND_ONLY" = true ]; then
    echo "Error: Cannot specify both --frontend-only and --backend-only"
    exit 1
fi

# Set verbosity
if [ "$VERBOSE" = true ]; then
    set -x
fi

# Function to check for required environment variables
check_env_vars() {
    local missing_vars=false
    
    # Common required variables
    if [ -z "$S3_BUCKET" ]; then
        echo "Error: S3_BUCKET environment variable is not set"
        missing_vars=true
    fi
    
    if [ -z "$S3_REGION" ]; then
        echo "Error: S3_REGION environment variable is not set"
        missing_vars=true
    fi
    
    # Target-specific required variables
    case $DEPLOYMENT_TARGET in
        amplify)
            if [ -z "$AMPLIFY_APP_ID" ]; then
                echo "Error: AMPLIFY_APP_ID environment variable is not set"
                missing_vars=true
            fi
            ;;
        eb)
            if [ -z "$EB_APPLICATION_NAME" ]; then
                echo "Error: EB_APPLICATION_NAME environment variable is not set"
                missing_vars=true
            fi
            ;;
        ecs)
            if [ -z "$ECS_CLUSTER" ]; then
                echo "Error: ECS_CLUSTER environment variable is not set"
                missing_vars=true
            fi
            ;;
    esac
    
    if [ "$missing_vars" = true ]; then
        echo "Please set the required environment variables and try again."
        exit 1
    fi
}

# Function to build and test the backend
build_backend() {
    echo "Building backend..."
    
    if [ "$SKIP_TESTS" = false ]; then
        echo "Running backend tests..."
        python -m pytest tests/
    fi
    
    # Additional backend build steps if needed
    pip install -e .
}

# Function to build the frontend
build_frontend() {
    echo "Building frontend..."
    
    cd s4-ui
    
    # Install dependencies
    npm install
    
    if [ "$SKIP_TESTS" = false ]; then
        echo "Running frontend tests..."
        npm test -- --watchAll=false
    fi
    
    # Build the frontend
    npm run build
    
    cd ..
}

# Function to deploy to Docker
deploy_docker() {
    echo "Deploying to Docker..."
    
    if [ "$AUTO_MODE" = true ]; then
        # Simple Docker deployment
        docker-compose build
        docker-compose up -d
    else
        # Interactive Docker deployment
        echo "Building Docker images..."
        docker-compose build
        
        echo "Starting Docker containers..."
        docker-compose up -d
        
        echo "Docker deployment complete. Services are now running."
        echo "Access the application at: http://localhost:8000"
    fi
}

# Function to deploy to AWS Amplify
deploy_amplify() {
    echo "Deploying to AWS Amplify..."
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed"
        exit 1
    fi
    
    # Deploy frontend to Amplify
    if [ "$BACKEND_ONLY" = false ]; then
        echo "Deploying frontend to Amplify..."
        
        cd s4-ui
        
        # Create zip file for deployment
        zip -r ../s4-ui-build.zip build
        
        cd ..
        
        # Start the deployment
        aws amplify start-deployment \
            --app-id "$AMPLIFY_APP_ID" \
            --branch-name main \
            --source-url s4-ui-build.zip
            
        echo "Frontend deployment to Amplify initiated"
    fi
    
    # Deploy backend if not frontend-only
    if [ "$FRONTEND_ONLY" = false ]; then
        echo "Deploying backend services..."
        
        # Backend deployment logic would go here
        # This would depend on your specific backend deployment strategy with Amplify
    fi
}

# Function to deploy to Elastic Beanstalk
deploy_eb() {
    echo "Deploying to AWS Elastic Beanstalk..."
    
    # Check for EB CLI
    if ! command -v eb &> /dev/null; then
        echo "Error: EB CLI is not installed"
        exit 1
    fi
    
    # Initialize EB if needed
    if [ ! -f ".elasticbeanstalk/config.yml" ]; then
        eb init "$EB_APPLICATION_NAME" --region "$S3_REGION" --platform "Python"
    fi
    
    # Deploy to EB
    eb deploy
}

# Function to deploy to ECS
deploy_ecs() {
    echo "Deploying to AWS ECS..."
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed"
        exit 1
    fi
    
    # Build and push Docker image to ECR
    aws ecr get-login-password --region "$S3_REGION" | docker login --username AWS --password-stdin "$ECR_REPOSITORY_URI"
    
    docker build -t s4-app .
    docker tag s4-app:latest "$ECR_REPOSITORY_URI:latest"
    docker push "$ECR_REPOSITORY_URI:latest"
    
    # Update ECS service
    aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" --force-new-deployment
}

# Main deployment logic
main() {
    echo "Starting S4 deployment to $DEPLOYMENT_TARGET..."
    
    # Check environment variables
    check_env_vars
    
    # Build steps
    if [ "$SKIP_BUILD" = false ]; then
        if [ "$FRONTEND_ONLY" = false ]; then
            build_backend
        fi
        
        if [ "$BACKEND_ONLY" = false ]; then
            build_frontend
        fi
    fi
    
    # Deploy based on target
    case $DEPLOYMENT_TARGET in
        docker)
            deploy_docker
            ;;
        amplify)
            deploy_amplify
            ;;
        eb)
            deploy_eb
            ;;
        ecs)
            deploy_ecs
            ;;
    esac
    
    echo "Deployment to $DEPLOYMENT_TARGET completed successfully!"
}

# Execute main function
main
