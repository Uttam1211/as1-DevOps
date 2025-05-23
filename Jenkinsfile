/*
 * Simple Jenkins Pipeline for Task Management System (Python Only)
 * Author: Uttam Thakur
 * Purpose: Basic CI/CD pipeline for Flask application without Docker
 * Date: 2025
 * Description: Simplified pipeline with essential stages for Python development
 */

pipeline {
    agent any
    
    // Define environment variables
    environment {
        // Application configuration
        APP_NAME = 'task-management-app'
        APP_PORT = '8000'
        PYTHON_VERSION = '3.11'
        
        // Deployment paths
        DEV_PATH = '/var/www/dev/task-management'
        STAGING_PATH = '/var/www/staging/task-management'
        PROD_PATH = '/var/www/prod/task-management'
    }
    
    // Build parameters
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution'
        )
        booleanParam(
            name: 'DEPLOY_APP',
            defaultValue: true,
            description: 'Deploy application after successful build'
        )
    }
    
    stages {
        stage('1. Checkout') {
            steps {
                echo "🔄 Starting CI/CD Pipeline for ${APP_NAME}"
                echo "📋 Build Number: ${BUILD_NUMBER}"
                echo "🎯 Target Environment: ${params.ENVIRONMENT}"
                
                // Clean workspace and checkout code
                cleanWs()
                checkout scm
                
                // Display Git information
                script {
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    def gitBranch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    echo "📂 Git Commit: ${gitCommit}"
                    echo "🌿 Git Branch: ${gitBranch}"
                }
            }
        }
        
        stage('2. Environment Setup') {
            steps {
                echo "🔧 Setting up Python virtual environment"
                
                sh '''
                    # Remove existing virtual environment if it exists
                    rm -rf venv
                    
                    # Create fresh virtual environment
                    python3 -m venv venv
                    
                    # Activate virtual environment and upgrade pip
                    . venv/bin/activate
                    pip install --upgrade pip
                    
                    # Install project dependencies
                    pip install -r requirements.txt
                    
                    # Verify installation
                    echo "Python version:"
                    python --version
                    echo "Installed packages:"
                    pip list
                '''
            }
        }
        
        stage('3. Code Quality Check') {
            steps {
                echo "🔍 Running code quality checks"
                
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    # Install code quality tools
                    pip install flake8 pylint
                    
                    # Run flake8 for PEP8 compliance
                    echo "Running flake8 code style check..."
                    flake8 app.py test_app.py --max-line-length=100 --statistics || true
                    
                    # Run basic pylint check
                    echo "Running pylint code quality check..."
                    pylint app.py --disable=missing-docstring,too-few-public-methods --score=yes || true
                '''
            }
        }
        
        stage('4. Unit Testing') {
            when {
                not { params.SKIP_TESTS }
            }
            steps {
                echo "🧪 Running unit tests"
                
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    # Install testing tools
                    pip install coverage
                    
                    # Run unit tests with verbose output
                    echo "Running unit tests..."
                    python -m unittest test_app.py -v
                    
                    # Run tests with coverage
                    echo "Running coverage analysis..."
                    python -m coverage run -m unittest test_app.py
                    python -m coverage report -m
                    
                    # Generate HTML coverage report
                    python -m coverage html
                '''
                
                // Publish HTML coverage report
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Test Coverage Report'
                ])
            }
        }
        
        stage('5. Security Scan') {
            steps {
                echo "🔒 Running security vulnerability scan"
                
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    # Install security tools
                    pip install safety bandit
                    
                    # Check for known vulnerabilities in dependencies
                    echo "Checking dependencies for security vulnerabilities..."
                    safety check || true
                    
                    # Run bandit for security issues in code
                    echo "Running bandit security scan..."
                    bandit -r app.py -f txt || true
                '''
            }
        }
        
        stage('6. Package Application') {
            steps {
                echo "📦 Packaging application for deployment"
                
                sh '''
                    # Create deployment package
                    echo "Creating deployment package..."
                    
                    # Create package directory
                    mkdir -p package
                    
                    # Copy application files
                    cp app.py package/
                    cp requirements.txt package/
                    
                    # Create startup script
                    cat > package/start.sh << 'EOF'
#!/bin/bash
# Startup script for Task Management System

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "Starting Task Management System..."
python app.py
EOF
                    
                    chmod +x package/start.sh
                    
                    echo "✅ Application packaged successfully"
                '''
                
                // Archive the package
                archiveArtifacts artifacts: 'package/**', fingerprint: true
            }
        }
        
        stage('7. Deploy Application') {
            when {
                expression { params.DEPLOY_APP }
            }
            steps {
                echo "🚀 Deploying application to ${params.ENVIRONMENT} environment"
                
                script {
                    def deployPath = ""
                    def deployPort = ""
                    
                    // Set environment-specific configurations
                    switch(params.ENVIRONMENT) {
                        case 'development':
                            deployPath = env.DEV_PATH
                            deployPort = '8000'
                            break
                        case 'staging':
                            deployPath = env.STAGING_PATH
                            deployPort = '8001'
                            break
                        case 'production':
                            deployPath = env.PROD_PATH
                            deployPort = '8002'
                            break
                    }
                    
                    sh """
                        echo "Deploying to: ${deployPath}"
                        echo "Port: ${deployPort}"
                        
                        # Create deployment directory if it doesn't exist
                        mkdir -p ${deployPath}
                        
                        # Stop existing application (if running)
                        echo "Stopping existing application..."
                        pkill -f "python.*app.py" || true
                        sleep 2
                        
                        # Copy application files to deployment directory
                        echo "Copying application files..."
                        cp -r package/* ${deployPath}/
                        cp -r venv ${deployPath}/
                        
                        # Set up environment variables
                        cd ${deployPath}
                        export FLASK_ENV=${params.ENVIRONMENT}
                        export PORT=${deployPort}
                        
                        # Start application in background
                        echo "Starting application..."
                        nohup ./start.sh > app.log 2>&1 &
                        
                        # Wait for application to start
                        sleep 5
                        
                        echo "✅ Application deployed successfully"
                        echo "🌐 Application should be available at: http://localhost:${deployPort}"
                    """
                }
            }
        }
        
        stage('8. Health Check') {
            when {
                expression { params.DEPLOY_APP }
            }
            steps {
                echo "🏥 Performing health check on deployed application"
                
                script {
                    def deployPort = params.ENVIRONMENT == 'production' ? '8002' : 
                                   params.ENVIRONMENT == 'staging' ? '8001' : '8000'
                    
                    sh """
                        # Wait for application to be fully ready
                        sleep 10
                        
                        # Check if application is responding
                        echo "Testing health endpoint..."
                        
                        # Try health check endpoint (with retry)
                        for i in {1..5}; do
                            if curl -s -f http://localhost:${deployPort}/health; then
                                echo ""
                                echo "✅ Health check passed!"
                                break
                            else
                                echo "Health check attempt \$i failed, retrying..."
                                sleep 5
                            fi
                            
                            if [ \$i -eq 5 ]; then
                                echo "❌ Health check failed after 5 attempts"
                                exit 1
                            fi
                        done
                        
                        # Test API endpoints
                        echo "Testing API endpoints..."
                        echo "GET /tasks:"
                        curl -s http://localhost:${deployPort}/tasks || true
                        
                        echo ""
                        echo "✅ Deployment verification completed successfully"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up build workspace"
            
            // Clean up temporary files
            sh '''
                # Remove temporary files but keep artifacts
                rm -rf htmlcov/.coverage
            '''
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
            
            // Send success notification
            script {
                def deployPort = params.ENVIRONMENT == 'production' ? '8002' : 
                               params.ENVIRONMENT == 'staging' ? '8001' : '8000'
                
                echo """
                🎉 Deployment Success Summary:
                - Build Number: ${BUILD_NUMBER}
                - Environment: ${params.ENVIRONMENT}
                - Application URL: http://localhost:${deployPort}
                - Health Check: http://localhost:${deployPort}/health
                """
            }
        }
        
        failure {
            echo "❌ Pipeline failed!"
            echo "Check the build logs for details: ${BUILD_URL}"
        }
        
        cleanup {
            // Final cleanup
            echo "🔄 Final cleanup completed"
        }
    }
} 