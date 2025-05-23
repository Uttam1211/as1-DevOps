#!/bin/bash

# Simple Deployment Script for Task Management System
# Author: Uttam Thakur
# Purpose: Deploy Flask application without Docker
# Date: 2025

set -e  # Exit on any error

# Configuration
APP_NAME="task-management-system"
DEFAULT_PORT=8000
VENV_DIR="venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -e, --env ENVIRONMENT    Set environment (development|staging|production)"
    echo "  -p, --port PORT         Set port number (default: 8000)"
    echo "  -d, --dir DIRECTORY     Set deployment directory"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --env development --port 8000"
    echo "  $0 --env production --port 8002 --dir /var/www/prod"
}

# Default values
ENVIRONMENT="development"
PORT=$DEFAULT_PORT
DEPLOY_DIR=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -d|--dir)
            DEPLOY_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Valid environments: development, staging, production"
    exit 1
fi

# Set default deployment directory if not provided
if [[ -z "$DEPLOY_DIR" ]]; then
    case $ENVIRONMENT in
        development)
            DEPLOY_DIR="/tmp/dev-task-management"
            ;;
        staging)
            DEPLOY_DIR="/tmp/staging-task-management"
            ;;
        production)
            DEPLOY_DIR="/tmp/prod-task-management"
            ;;
    esac
fi

print_status "Starting deployment..."
print_status "Environment: $ENVIRONMENT"
print_status "Port: $PORT"
print_status "Deploy Directory: $DEPLOY_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed or not in PATH"
    exit 1
fi

print_success "Python3 found: $(python3 --version)"

# Check if required files exist
if [[ ! -f "app.py" ]]; then
    print_error "app.py not found in current directory"
    exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
    print_error "requirements.txt not found in current directory"
    exit 1
fi

print_success "Required files found"

# Stop existing application if running
print_status "Stopping existing application processes..."
pkill -f "python.*app.py" || true
sleep 2

# Create deployment directory
print_status "Creating deployment directory: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy application files
print_status "Copying application files..."
cp app.py "$DEPLOY_DIR/"
cp requirements.txt "$DEPLOY_DIR/"

if [[ -f "test_app.py" ]]; then
    cp test_app.py "$DEPLOY_DIR/"
fi

# Change to deployment directory
cd "$DEPLOY_DIR"

# Create virtual environment
print_status "Setting up virtual environment..."
if [[ -d "$VENV_DIR" ]]; then
    print_warning "Removing existing virtual environment"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip and install dependencies
print_status "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

print_success "Dependencies installed successfully"

# Run tests if test file exists
if [[ -f "test_app.py" ]]; then
    print_status "Running tests..."
    if python -m unittest test_app.py -v; then
        print_success "All tests passed"
    else
        print_error "Tests failed"
        exit 1
    fi
fi

# Create startup script
print_status "Creating startup script..."
cat > start_app.sh << EOF
#!/bin/bash
# Auto-generated startup script

# Set environment variables
export FLASK_ENV=$ENVIRONMENT
export PORT=$PORT

# Activate virtual environment
source $VENV_DIR/bin/activate

# Start the application
echo "Starting Task Management System on port $PORT..."
python app.py
EOF

chmod +x start_app.sh

# Create stop script
cat > stop_app.sh << EOF
#!/bin/bash
# Auto-generated stop script

echo "Stopping Task Management System..."
pkill -f "python.*app.py" || echo "No running application found"
EOF

chmod +x stop_app.sh

# Set environment variables
export FLASK_ENV=$ENVIRONMENT
export PORT=$PORT

# Start application in background
print_status "Starting application..."
nohup ./start_app.sh > app.log 2>&1 &
APP_PID=$!

# Wait for application to start
sleep 3

# Check if application is running
if ps -p $APP_PID > /dev/null; then
    print_success "Application started successfully"
    print_success "PID: $APP_PID"
    print_success "Log file: $DEPLOY_DIR/app.log"
    print_success "Application URL: http://localhost:$PORT"
    print_success "Health check: http://localhost:$PORT/health"
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    sleep 2
    
    if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
        print_success "Health check passed!"
    else
        print_warning "Health check failed - application might still be starting"
    fi
    
    echo ""
    print_status "Deployment completed successfully!"
    print_status "To stop the application, run: $DEPLOY_DIR/stop_app.sh"
    print_status "To view logs, run: tail -f $DEPLOY_DIR/app.log"
    
else
    print_error "Failed to start application"
    print_error "Check the log file: $DEPLOY_DIR/app.log"
    exit 1
fi