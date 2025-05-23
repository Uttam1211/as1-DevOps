/*
 * Jenkins CI/CD Pipeline for Task Management System
 * 
 * Author: Uttam Thakur
 * Course: CSY3056 - Development Operations and Software Testing
 * University: University of Northampton
 * Date: 2025
 * 
 * This pipeline implements automated CI/CD for a Python Flask application
 * featuring branch-based environment detection, automated testing, security
 * scanning, and deployment with health verification.
 */

pipeline {
    agent any
    
    environment {
        // Application configuration
        APP_NAME = 'task-management-app'
        PYTHON_VERSION = '3.11'
        
        // Environment-specific deployment paths
        DEV_PATH = '/var/www/dev/task-management'
        STAGING_PATH = '/var/www/staging/task-management'
        PROD_PATH = '/var/www/prod/task-management'
        
        // Runtime variables (set dynamically based on branch)
        DEPLOY_ENVIRONMENT = ''
        DEPLOY_PORT = ''
    }
    
    // Automated triggers for continuous integration
    triggers {
        pollSCM('H/5 * * * *')  // Poll SCM every 5 minutes
        githubPush()            // Trigger on Git webhook events
    }
    
    stages {
        
        stage('Checkout and Environment Detection') {
            steps {
                script {
                    // Clean workspace for consistent builds
                    cleanWs()
                    
                    // Checkout source code from SCM
                    checkout scm
                    
                    // Extract Git information for environment detection
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    def gitBranch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    
                    // Determine deployment environment based on Git branch
                    // Production: main/master branches
                    // Staging: develop/staging branches  
                    // Development: all other branches
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
                    
                    echo "Build: ${BUILD_NUMBER}, Branch: ${gitBranch}, Environment: ${env.DEPLOY_ENVIRONMENT}"
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    // Remove any existing virtual environment
                    sh 'rm -rf venv'
                    
                    // Create fresh Python virtual environment
                    sh 'python -m venv venv'
                    
                    // Install dependencies in isolated environment
                    sh '''
                        . venv/bin/activate
                        pip install --upgrade pip --quiet
                        pip install -r requirements.txt --quiet
                    '''
                    
                    // Verify environment setup
                    sh '''
                        . venv/bin/activate
                        python --version
                        pip list --format=freeze | wc -l
                    '''
                }
            }
        }
        
        stage('Code Quality Analysis') {
            steps {
                script {
                    // Install code quality tools
                    sh '''
                        . venv/bin/activate
                        pip install flake8 pylint --quiet
                    '''
                    
                    // Run PEP8 compliance check
                    sh '''
                        . venv/bin/activate
                        flake8 app.py test_app.py --max-line-length=100 --statistics || true
                    '''
                    
                    // Run code quality analysis
                    sh '''
                        . venv/bin/activate
                        pylint app.py --disable=missing-docstring,too-few-public-methods --score=yes || true
                    '''
                }
            }
        }
        
        stage('Automated Testing') {
            steps {
                script {
                    // Install testing dependencies
                    sh '''
                        . venv/bin/activate
                        pip install coverage --quiet
                    '''
                    
                    // Execute unit test suite
                    sh '''
                        . venv/bin/activate
                        python -m unittest test_app.py -v
                    '''
                    
                    // Generate test coverage analysis
                    sh '''
                        . venv/bin/activate
                        python -m coverage run -m unittest test_app.py
                        python -m coverage report -m
                        python -m coverage html
                    '''
                }
                
                // Archive coverage reports (works without additional plugins)
                script {
                    // Archive HTML coverage report as build artifact
                    if (fileExists('htmlcov')) {
                        archiveArtifacts artifacts: 'htmlcov/**', fingerprint: true, allowEmptyArchive: true
                        echo "Coverage report archived as build artifact"
                        echo "Access via: ${BUILD_URL}artifact/htmlcov/index.html"
                    } else {
                        echo "Coverage HTML report not generated"
                    }
                }
            }
        }
        
        stage('Security Scanning') {
            steps {
                script {
                    // Install security analysis tools
                    sh '''
                        . venv/bin/activate
                        pip install safety bandit --quiet
                    '''
                    
                    // Check dependencies for known vulnerabilities
                    sh '''
                        . venv/bin/activate
                        safety check || true
                    '''
                    
                    // Perform static security analysis on source code
                    sh '''
                        . venv/bin/activate
                        bandit -r app.py -f txt || true
                    '''
                }
            }
        }
        
        stage('Application Packaging') {
            steps {
                script {
                    // Create deployment package structure
                    sh 'mkdir -p package'
                    
                    // Copy application files
                    sh '''
                        cp app.py package/
                        cp requirements.txt package/
                    '''
                    
                    // Generate environment-specific startup script
                    sh """
                        cat > package/start.sh << 'EOF'
#!/bin/bash
# Startup script for application

# Use environment variables passed at runtime
export FLASK_ENV=\${FLASK_ENV:-development}
export PORT=\${PORT:-8000}

echo "Starting application with FLASK_ENV=\$FLASK_ENV on PORT=\$PORT"

source venv/bin/activate
python app.py
EOF
                        chmod +x package/start.sh
                    """
                    
                    // Generate application stop script
                    sh '''
                        cat > package/stop.sh << EOF
#!/bin/bash
# Stop script for application shutdown

pkill -f "python.*app.py" || echo "No running application found"
EOF
                        chmod +x package/stop.sh
                    '''
                }
                
                // Archive build artifacts
                archiveArtifacts artifacts: 'package/**', fingerprint: true
            }
        }
        
        stage('Deployment') {
            steps {
                script {
                    // Determine deployment path based on environment
                    def deployPath = ""
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
                        default:
                            deployPath = env.DEV_PATH
                            break
                    }
                    
                    // Validate environment variables are set
                    if (!env.DEPLOY_ENVIRONMENT || !env.DEPLOY_PORT) {
                        error("Environment variables not properly set: DEPLOY_ENVIRONMENT=${env.DEPLOY_ENVIRONMENT}, DEPLOY_PORT=${env.DEPLOY_PORT}")
                    }
                    
                    echo "Deploying to environment: ${env.DEPLOY_ENVIRONMENT}"
                    echo "Target path: ${deployPath}"
                    echo "Target port: ${env.DEPLOY_PORT}"
                    
                    // Execute deployment process with proper variable handling
                    sh """
                        # Set deployment variables
                        DEPLOY_PATH="${deployPath}"
                        TARGET_ENV="${env.DEPLOY_ENVIRONMENT}"
                        TARGET_PORT="${env.DEPLOY_PORT}"
                        
                        echo "Starting deployment to: \$DEPLOY_PATH"
                        echo "Environment: \$TARGET_ENV"
                        echo "Port: \$TARGET_PORT"
                        
                        # Create deployment directory
                        mkdir -p "\$DEPLOY_PATH"
                        
                        # Stop existing application instance
                        echo "Stopping existing application..."
                        pkill -f "python.*app.py" || true
                        sleep 2
                        
                        # Deploy application files
                        echo "Deploying application files..."
                        cp -r package/* "\$DEPLOY_PATH/"
                        cp -r venv "\$DEPLOY_PATH/"
                        
                        # Start application with environment configuration
                        echo "Starting application..."
                        cd "\$DEPLOY_PATH"
                        export FLASK_ENV="\$TARGET_ENV"
                        export PORT="\$TARGET_PORT"
                        nohup ./start.sh > app.log 2>&1 &
                        
                        sleep 5
                        echo "Deployment process completed"
                    """
                    
                    echo "Deployment completed: ${env.DEPLOY_ENVIRONMENT} environment on port ${env.DEPLOY_PORT}"
                }
            }
        }
        
        stage('Health Verification') {
            steps {
                script {
                    // Wait for application startup
                    sh 'sleep 10'
                    
                    // Verify application health with retry logic
                    sh """
                        for i in {1..5}; do
                            if curl -s -f http://localhost:${env.DEPLOY_PORT}/health; then
                                echo "Health check passed"
                                break
                            else
                                echo "Health check attempt \$i failed"
                                if [ \$i -eq 5 ]; then
                                    echo "Health verification failed after 5 attempts"
                                    exit 1
                                fi
                                sleep 5
                            fi
                        done
                    """
                    
                    // Verify API endpoints functionality
                    sh """
                        curl -s http://localhost:${env.DEPLOY_PORT}/tasks | head -c 100
                    """
                    
                    echo "Health verification completed successfully"
                }
            }
        }
    }
    
    post {
        always {
            // Clean up temporary build artifacts
            sh 'rm -rf .coverage 2>/dev/null || true'
        }
        
        success {
            script {
                echo """
                Deployment Summary:
                - Build: ${BUILD_NUMBER}
                - Environment: ${env.DEPLOY_ENVIRONMENT}
                - Port: ${env.DEPLOY_PORT}
                - URL: http://localhost:${env.DEPLOY_PORT}
                """
                
                // Send email notification if configured
                try {
                    mail to: 'devops@company.com',
                         subject: "Deployment Success: ${APP_NAME} [${env.DEPLOY_ENVIRONMENT}] - Build ${BUILD_NUMBER}",
                         body: """
                         Deployment completed successfully.
                         
                         Environment: ${env.DEPLOY_ENVIRONMENT}
                         Application URL: http://localhost:${env.DEPLOY_PORT}
                         Build Details: ${BUILD_URL}
                         """
                } catch (Exception e) {
                    echo "Email notification not configured"
                }
            }
        }
        
        failure {
            script {
                echo "Pipeline failed - Build ${BUILD_NUMBER}"
                
                // Send failure notification if configured
                try {
                    mail to: 'devops@company.com',
                         subject: "Deployment Failed: ${APP_NAME} [${env.DEPLOY_ENVIRONMENT}] - Build ${BUILD_NUMBER}",
                         body: """
                         Pipeline execution failed.
                         
                         Build Details: ${BUILD_URL}
                         Environment: ${env.DEPLOY_ENVIRONMENT ?: 'Unknown'}
                         """
                } catch (Exception e) {
                    echo "Email notification not configured"
                }
            }
        }
        
        cleanup {
            echo "Pipeline cleanup completed"
        }
    }
} 