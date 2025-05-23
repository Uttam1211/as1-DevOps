/*
 * Jenkins CI/CD Pipeline for Task Management System (Development Environment)
 * 
 * Author: Uttam Thakur
 * Course: CSY3056 - Development Operations and Software Testing
 * University: University of Northampton
 * Date: 2025
 * 
 * This pipeline implements automated CI/CD for a Python Flask application
 * featuring automated testing, security scanning, and deployment to development environment.
 * 
 * NOTE: For other environments (staging, production), separate pipeline files are used:
 * - Jenkinsfile_staging (deploys to staging environment)
 * - Jenkinsfile_prod (deploys to production environment)
 * This ensures environment-specific configurations and deployment strategies.
 */

pipeline {
    agent any
    
    environment {
        // Application configuration
        APP_NAME = 'task-management-app'
        PYTHON_VERSION = '3.11'
        
        // Fixed deployment configuration (development environment)
        DEPLOY_PATH = '/var/www/dev/task-management'
        DEPLOY_PORT = '8000'
        FLASK_ENV = 'development'
    }
    
    // Automated triggers for continuous integration
    triggers {
        pollSCM('H/5 * * * *')  // Poll SCM every 5 minutes
        githubPush()            // Trigger on Git webhook events
    }
    
    stages {
        
        stage('Checkout') {
            steps {
                script {
                    // Clean workspace for consistent builds
                    cleanWs()
                    
                    // Checkout source code from SCM
                    checkout scm
                    
                    // Extract Git information for logging
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    def gitBranch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    
                    echo "Build ${BUILD_NUMBER}: ${gitBranch}@${gitCommit} -> Development:8000"
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
                        echo "Python $(python --version | cut -d' ' -f2) with $(pip list --format=freeze | wc -l) packages installed"
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
                
                // Archive coverage reports
                script {
                    // Archive HTML coverage report as build artifact
                    if (fileExists('htmlcov')) {
                        archiveArtifacts artifacts: 'htmlcov/**', fingerprint: true, allowEmptyArchive: true
                        echo "Coverage report archived at ${BUILD_URL}artifact/htmlcov/index.html"
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
                    
                    // Generate startup script
                    sh '''
                        cat > package/start.sh << 'EOF'
#!/bin/bash
# Startup script for development environment

export FLASK_ENV=development
export PORT=8000

echo "Starting Task Management App in development mode on port 8000"

source venv/bin/activate
python app.py
EOF
                        chmod +x package/start.sh
                    '''
                    
                    // Generate stop script
                    sh '''
                        cat > package/stop.sh << 'EOF'
#!/bin/bash
# Stop script for application shutdown

echo "Stopping Task Management App..."
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
                    echo "Deploying to ${DEPLOY_PATH} on port ${DEPLOY_PORT}"
                    
                    // Execute deployment process
                    sh '''
                        # Create deployment directory
                        mkdir -p "${DEPLOY_PATH}"
                        
                        # Stop existing application instance
                        pkill -f "python.*app.py" || true
                        sleep 3
                        
                        # Deploy application files
                        cp -r package/* "${DEPLOY_PATH}/"
                        cp -r venv "${DEPLOY_PATH}/"
                        
                        # Start application
                        cd "${DEPLOY_PATH}"
                        nohup ./start.sh > app.log 2>&1 &
                        
                        sleep 5
                    '''
                    
                    echo "Application deployed successfully"
                }
            }
        }
        
        stage('Health Verification') {
            steps {
                script {
                    // Wait for application startup
                    sh 'sleep 10'
                    
                    // Verify application health with retry logic
                    sh '''
                        for i in {1..5}; do
                            if curl -s -f http://localhost:8000/health; then
                                echo "Health check passed"
                                break
                            else
                                if [ $i -eq 5 ]; then
                                    echo "Health verification failed after 5 attempts"
                                    exit 1
                                fi
                                sleep 5
                            fi
                        done
                    '''
                    
                    // Verify API endpoints functionality
                    sh '''
                        curl -s http://localhost:8000/tasks | head -c 100
                    '''
                    
                    echo "Health verification completed"
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
                echo "Deployment successful: Build ${BUILD_NUMBER} deployed to http://localhost:8000"
                
                }
            }
        }
        
        failure {
            script {
                echo "Deployment failed: Build ${BUILD_NUMBER} - Check logs at ${BUILD_URL}console"

                // Send email notification if configured, will implement when smtp is set up
                
            }
        }
        
        cleanup {
            echo "Pipeline cleanup completed"
        }
    }
} 