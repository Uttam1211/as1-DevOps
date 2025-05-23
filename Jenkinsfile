/*
 * Automated Jenkins Pipeline for Task Management System (Python Only)
 * Author: Uttam Thakur
 * Purpose: Fully automated CI/CD pipeline for Flask application without Docker
 * Date: 2025
 * Description: Automated pipeline with environment selection based on Git branch
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
        
        // Auto-determined environment (will be set based on branch)
        DEPLOY_ENVIRONMENT = ''
        DEPLOY_PORT = ''
    }
    
    // Configure automatic triggers
    triggers {
        // Poll SCM every 5 minutes for changes
        pollSCM('H/5 * * * *')
        // Trigger on push events
        githubPush()
    }
    
    stages {
        stage('1. Checkout & Environment Detection') {
            steps {
                echo "🔄 Starting Automated CI/CD Pipeline for ${APP_NAME}"
                echo "📋 Build Number: ${BUILD_NUMBER}"
                
                // Clean workspace and checkout code
                cleanWs()
                checkout scm
                
                // Automatically determine environment based on Git branch
                script {
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    def gitBranch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    
                    echo "📂 Git Commit: ${gitCommit}"
                    echo "🌿 Git Branch: ${gitBranch}"
                    
                    // Determine environment and port based on branch
                    if (gitBranch == 'main' || gitBranch == 'master') {
                        env.DEPLOY_ENVIRONMENT = 'production'
                        env.DEPLOY_PORT = '8002'
                    } else if (gitBranch == 'develop' || gitBranch == 'staging') {
                        env.DEPLOY_ENVIRONMENT = 'staging'
                        env.DEPLOY_PORT = '8001'
                    } else {
                        env.DEPLOY_ENVIRONMENT = 'development'
                        env.DEPLOY_PORT = '8000'
                    }
                    
                    echo "🎯 Auto-detected Environment: ${env.DEPLOY_ENVIRONMENT}"
                    echo "🚢 Target Port: ${env.DEPLOY_PORT}"
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
                    python -m venv venv
                    
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
                echo "🔍 Running automated code quality checks"
                
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
        
        stage('4. Automated Testing') {
            steps {
                echo "🧪 Running automated unit tests with coverage"
                
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    # Install testing tools
                    pip install coverage
                    
                    # Run unit tests with verbose output
                    echo "Running all unit tests..."
                    python -m unittest test_app.py -v
                    
                    # Run tests with coverage analysis
                    echo "Generating coverage report..."
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
                echo "🔒 Running automated security vulnerability scan"
                
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
                echo "📦 Packaging application for automated deployment"
                
                sh '''
                    # Create deployment package
                    echo "Creating deployment package..."
                    
                    # Create package directory
                    mkdir -p package
                    
                    # Copy application files
                    cp app.py package/
                    cp requirements.txt package/
                    
                    # Create environment-specific startup script
                    cat > package/start.sh << EOF
#!/bin/bash
# Auto-generated startup script for ${DEPLOY_ENVIRONMENT} environment

# Set environment variables
export FLASK_ENV=${DEPLOY_ENVIRONMENT}
export PORT=${DEPLOY_PORT}

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "Starting Task Management System on port ${DEPLOY_PORT} in ${DEPLOY_ENVIRONMENT} mode..."
python app.py
EOF
                    
                    chmod +x package/start.sh
                    
                    # Create stop script
                    cat > package/stop.sh << EOF
#!/bin/bash
# Auto-generated stop script

echo "Stopping Task Management System..."
pkill -f "python.*app.py" || echo "No running application found"
EOF
                    
                    chmod +x package/stop.sh
                    
                    echo "✅ Application packaged for ${DEPLOY_ENVIRONMENT} environment"
                '''
                
                // Archive the package
                archiveArtifacts artifacts: 'package/**', fingerprint: true
            }
        }
        
        stage('7. Automated Deployment') {
            steps {
                echo "🚀 Deploying application to ${env.DEPLOY_ENVIRONMENT} environment"
                
                script {
                    def deployPath = ""
                    
                    // Set deployment path based on environment
                    switch(env.DEPLOY_ENVIRONMENT) {
                        case 'development':
                            deployPath = env.DEV_PATH
                            break
                        case 'staging':
                            deployPath = env.STAGING_PATH
                            break
                        case 'production':
                            deployPath = env.PROD_PATH
                            break
                    }
                    
                    sh """
                        echo "Deploying to: ${deployPath}"
                        echo "Environment: ${env.DEPLOY_ENVIRONMENT}"
                        echo "Port: ${env.DEPLOY_PORT}"
                        
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
                        
                        # Set up environment for deployment
                        cd ${deployPath}
                        export FLASK_ENV=${env.DEPLOY_ENVIRONMENT}
                        export PORT=${env.DEPLOY_PORT}
                        
                        # Start application in background
                        echo "Starting application..."
                        nohup ./start.sh > app.log 2>&1 &
                        
                        # Wait for application to start
                        sleep 5
                        
                        echo "✅ Application deployed successfully"
                        echo "🌐 Application URL: http://localhost:${env.DEPLOY_PORT}"
                        echo "📁 Deployment path: ${deployPath}"
                    """
                }
            }
        }
        
        stage('8. Automated Health Check') {
            steps {
                echo "🏥 Performing automated health verification"
                
                script {
                    sh """
                        # Wait for application to be fully ready
                        sleep 10
                        
                        # Check if application is responding
                        echo "Testing health endpoint at http://localhost:${env.DEPLOY_PORT}/health"
                        
                        # Try health check endpoint with retry logic
                        for i in {1..5}; do
                            if curl -s -f http://localhost:${env.DEPLOY_PORT}/health; then
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
                        
                        # Test additional API endpoints
                        echo ""
                        echo "Testing API endpoints..."
                        echo "GET /tasks:"
                        curl -s http://localhost:${env.DEPLOY_PORT}/tasks | head -c 100
                        
                        echo ""
                        echo "✅ All health checks passed - deployment verified!"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up build workspace"
            
            // Clean up temporary files but keep important artifacts
            sh '''
                # Remove temporary files but keep coverage reports
                rm -rf .coverage 2>/dev/null || true
            '''
        }
        
        success {
            echo "✅ Automated pipeline completed successfully!"
            
            script {
                echo """
                🎉 Deployment Success Summary:
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📋 Build Number: ${BUILD_NUMBER}
                🌿 Git Branch: ${env.BRANCH_NAME ?: 'N/A'}
                🎯 Environment: ${env.DEPLOY_ENVIRONMENT}
                🚢 Port: ${env.DEPLOY_PORT}
                🌐 Application URL: http://localhost:${env.DEPLOY_PORT}
                🏥 Health Check: http://localhost:${env.DEPLOY_PORT}/health
                📊 Coverage Report: ${BUILD_URL}Test_Coverage_Report/
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """
                
                // Send notification (if email configured)
                try {
                    mail to: 'devops@company.com',
                         subject: "✅ Auto-Deployment Success: ${APP_NAME} [${env.DEPLOY_ENVIRONMENT}] - Build #${BUILD_NUMBER}",
                         body: """
                         Automated deployment completed successfully!
                         
                         Environment: ${env.DEPLOY_ENVIRONMENT}
                         Application URL: http://localhost:${env.DEPLOY_PORT}
                         Git Branch: ${env.BRANCH_NAME ?: 'N/A'}
                         
                         View build details: ${BUILD_URL}
                         """
                } catch (Exception e) {
                    echo "📧 Email notification not configured (${e.getMessage()})"
                }
            }
        }
        
        failure {
            echo "❌ Automated pipeline failed!"
            
            script {
                echo """
                💥 Pipeline Failure Details:
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📋 Build Number: ${BUILD_NUMBER}
                🌿 Git Branch: ${env.BRANCH_NAME ?: 'N/A'}
                🎯 Target Environment: ${env.DEPLOY_ENVIRONMENT ?: 'Unknown'}
                🔗 Build URL: ${BUILD_URL}
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """
                
                // Send failure notification (if email configured)
                try {
                    mail to: 'devops@company.com',
                         subject: "❌ Auto-Deployment Failed: ${APP_NAME} [${env.DEPLOY_ENVIRONMENT ?: 'Unknown'}] - Build #${BUILD_NUMBER}",
                         body: """
                         Automated deployment failed!
                         
                         Please check the build logs for details: ${BUILD_URL}
                         
                         Branch: ${env.BRANCH_NAME ?: 'N/A'}
                         Target Environment: ${env.DEPLOY_ENVIRONMENT ?: 'Unknown'}
                         """
                } catch (Exception e) {
                    echo "📧 Email notification not configured (${e.getMessage()})"
                }
            }
        }
        
        cleanup {
            echo "🔄 Final automated cleanup completed"
        }
    }
} 