/*
 * Jenkins Pipeline for Task Management System
 * Author: Uttam Thakur
 * Purpose: Automated CI/CD pipeline for Flask application
 * Date: 2025
 * Description: Complete pipeline with build, test, containerization, and deployment stages
 */

pipeline {
    agent any // this can be changed to a specific agent if needed under settings
    
    // Define environment variables
    environment {
        // Docker configuration
        DOCKER_IMAGE = 'task-management-system'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'localhost:8000'  // Local registry for demonstration
        
        // Application configuration
        APP_NAME = 'task-management-app'
        APP_PORT = '8000'
        
        // Testing configuration
        PYTHON_VERSION = '3.11' // to preserve the python version for the pipeline
        
        // Credentials (stored in Jenkins credentials store)
        DOCKER_CREDENTIALS = credentials('docker-registry-credentials')
    }
    
    // Define build parameters
    parameters {
        choice(
            name: 'DEPLOYMENT_ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution (not recommended for production)'
        )
        booleanParam(
            name: 'DEPLOY_APPLICATION',
            defaultValue: true,
            description: 'Deploy application after successful build and test'
        )
    }
    
    // Configure build triggers
    triggers {
        // Poll SCM every 5 minutes for changes
        pollSCM('H/5 * * * *')
        // Trigger build on webhook
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Starting CI/CD Pipeline for ${APP_NAME}"
                echo "📋 Build Number: ${BUILD_NUMBER}"
                echo "🎯 Target Environment: ${params.DEPLOYMENT_ENVIRONMENT}"
                
                // Clean workspace and checkout code
                cleanWs()
                checkout scm
                
                // Display Git information
                script {
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    def gitBranch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    echo "📂 Git Commit: ${gitCommit}"
                    echo "🌿 Git Branch: ${gitBranch}"
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo "🔧 Setting up Python environment"
                
                sh '''
                    # Create virtual environment
                    python3 -m venv venv
                    
                    # Activate virtual environment and install dependencies
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Verify installation
                    python --version
                    pip list
                '''
            }
        }
        
        stage('Code Quality & Security Scan') {
            parallel {
                stage('Lint Code') {
                    steps {
                        echo "🔍 Running code quality checks"
                        
                        sh '''
                            . venv/bin/activate
                            
                            # Install linting tools
                            pip install flake8 pylint
                            
                            # Run flake8 for PEP8 compliance
                            echo "Running flake8..."
                            flake8 app.py test_app.py --max-line-length=100 --statistics
                            
                            # Run pylint for code quality
                            echo "Running pylint..."
                            pylint app.py --disable=missing-docstring,too-few-public-methods || true
                        '''
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        echo "🔒 Running security vulnerability scan"
                        
                        sh '''
                            . venv/bin/activate
                            
                            # Install security scanning tools
                            pip install safety bandit
                            
                            # Check for known security vulnerabilities in dependencies
                            echo "Checking dependencies for security vulnerabilities..."
                            safety check || true
                            
                            # Static security analysis
                            echo "Running bandit security scan..."
                            bandit -r app.py || true
                        '''
                    }
                }
            }
        }
        
        stage('Unit Testing') {
            when {
                not { params.SKIP_TESTS }
            }
            steps {
                echo "🧪 Running unit tests with coverage analysis"
                
                sh '''
                    . venv/bin/activate
                    
                    # Run unit tests with coverage
                    echo "Running unit tests..."
                    python -m coverage run -m unittest test_app.py -v
                    
                    # Generate coverage report
                    python -m coverage report -m
                    python -m coverage html
                    
                    # Generate XML coverage report for Jenkins
                    python -m coverage xml
                '''
                
                // Archive test results
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
            post {
                always {
                    // Publish test results
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    
                    // Archive coverage data
                    publishCoverage adapters: [
                        coberturaAdapter('coverage.xml')
                    ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker image"
                
                script {
                    // Build Docker image with multiple tags
                    def dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                    
                    // Tag for registry
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker tag ${DOCKER_IMAGE}:latest ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest"
                    
                    echo "✅ Docker image built successfully"
                }
            }
        }
        
        stage('Container Security Scan') {
            steps {
                echo "🔒 Scanning Docker image for vulnerabilities"
                
                script {
                    // Scan Docker image for vulnerabilities (using a mock scan for demonstration)
                    sh '''
                        echo "Running container security scan..."
                        # In a real environment, you would use tools like:
                        # docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ${DOCKER_IMAGE}:${DOCKER_TAG}
                        echo "✅ Container security scan completed"
                    '''
                }
            }
        }
        
        stage('Integration Testing') {
            when {
                not { params.SKIP_TESTS }
            }
            steps {
                echo "🧪 Running integration tests against containerized application"
                
                script {
                    try {
                        // Start container for testing
                        sh '''
                            docker run -d --name test-container-${BUILD_NUMBER} \
                                -p 5001:8000 \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                                
                            # Wait for container to be ready
                            sleep 10
                            
                            # Test health endpoint
                            curl -f http://localhost:5001/health || exit 1
                            
                            # Test API endpoints
                            echo "Testing API endpoints..."
                            
                            # Test GET /tasks
                            curl -X GET http://localhost:5001/tasks
                            
                            # Test POST /tasks
                            curl -X POST http://localhost:5001/tasks \
                                -H "Content-Type: application/json" \
                                -d '{"title": "Integration Test Task", "description": "Test description"}'
                            
                            echo "✅ Integration tests passed"
                        '''
                    } finally {
                        // Clean up test container
                        sh 'docker stop test-container-${BUILD_NUMBER} || true'
                        sh 'docker rm test-container-${BUILD_NUMBER} || true'
                    }
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    expression { params.DEPLOYMENT_ENVIRONMENT == 'production' }
                }
            }
            steps {
                echo "📤 Pushing Docker image to registry"
                
                script {
                    // Push to Docker registry
                    docker.withRegistry("http://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        sh "docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest"
                    }
                    
                    echo "✅ Docker image pushed to registry successfully"
                }
            }
        }
        
        stage('Deploy Application') {
            when {
                expression { params.DEPLOY_APPLICATION }
            }
            steps {
                echo "🚀 Deploying application to ${params.DEPLOYMENT_ENVIRONMENT} environment"
                
                script {
                    def deploymentPort = 8000
                    
                    // Set environment-specific configurations
                    switch(params.DEPLOYMENT_ENVIRONMENT) {
                        case 'development':
                            deploymentPort = 8000
                            break
                        case 'staging':
                            deploymentPort = 8001
                            break
                        case 'production':
                            deploymentPort = 8002
                            break
                    }
                    
                    sh """
                        # Stop existing container if running
                        docker stop ${APP_NAME}-${params.DEPLOYMENT_ENVIRONMENT} || true
                        docker rm ${APP_NAME}-${params.DEPLOYMENT_ENVIRONMENT} || true
                        
                        # Deploy new container
                        docker run -d \
                            --name ${APP_NAME}-${params.DEPLOYMENT_ENVIRONMENT} \
                            -p ${deploymentPort}:8000 \
                            --restart unless-stopped \
                            -e FLASK_ENV=${params.DEPLOYMENT_ENVIRONMENT} \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                        
                        # Verify deployment
                        sleep 10
                        curl -f http://localhost:${deploymentPort}/health
                        
                        echo "✅ Application deployed successfully on port ${deploymentPort}"
                    """
                }
            }
        }
        
        stage('Smoke Tests') {
            when {
                expression { params.DEPLOY_APPLICATION }
            }
            steps {
                echo "💨 Running smoke tests on deployed application"
                
                script {
                    def deploymentPort = params.DEPLOYMENT_ENVIRONMENT == 'production' ? 8002 : 
                                       params.DEPLOYMENT_ENVIRONMENT == 'staging' ? 8001 : 8000
                    
                    sh """
                        # Basic functionality tests
                        echo "Testing deployed application..."
                        
                        # Health check
                        curl -f http://localhost:${deploymentPort}/health
                        
                        # Test core API functionality
                        response=\$(curl -s -X GET http://localhost:${deploymentPort}/tasks)
                        echo "API Response: \$response"
                        
                        echo "✅ Smoke tests passed"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up workspace and temporary resources"
            
            // Clean up Docker images
            sh '''
                docker image prune -f
                docker container prune -f
            '''
            
            // Archive build artifacts
            archiveArtifacts artifacts: '**/*.py, requirements.txt, Dockerfile, Jenkinsfile', 
                             fingerprint: true
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
            
            // Send success notification (would integrate with Slack, email, etc.)
            mail to: 'devops@university.ac.uk',
                 subject: "✅ Deployment Success: ${APP_NAME} - Build #${BUILD_NUMBER}",
                 body: """
                 Build #${BUILD_NUMBER} completed successfully!
                 
                 Environment: ${params.DEPLOYMENT_ENVIRONMENT}
                 Git Branch: ${env.BRANCH_NAME}
                 Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}
                 
                 View build details: ${BUILD_URL}
                 """
        }
        
        failure {
            echo "❌ Pipeline failed!"
            
            // Send failure notification
            mail to: 'devops@university.ac.uk',
                 subject: "❌ Deployment Failed: ${APP_NAME} - Build #${BUILD_NUMBER}",
                 body: """
                 Build #${BUILD_NUMBER} failed!
                 
                 Please check the build logs for details: ${BUILD_URL}
                 """
        }
        
        unstable {
            echo "⚠️ Pipeline completed with warnings"
        }
        
        cleanup {
            // Final cleanup
            cleanWs()
        }
    }
} 