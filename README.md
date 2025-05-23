# Task Management System - DevOps Project

**Author:** Student Name  
**Course:** CSY3056 - Development Operations and Software Testing  
**University:** University of Northampton  
**Date:** 2025

## 📋 Project Overview

This project demonstrates a complete DevOps implementation featuring a Flask-based Task Management System with comprehensive CI/CD pipeline, containerization, and automated testing. The project showcases industry best practices in software development, testing, and deployment automation.

### 🎯 Key Features

- **Modular Flask Application** with RESTful API design
- **Comprehensive Test Suite** following TDD principles
- **Docker Containerization** for consistent deployments
- **Jenkins CI/CD Pipeline** with automated build, test, and deploy stages
- **Multi-environment Support** (Development, Staging, Production)
- **Security Integration** with vulnerability scanning and code analysis
- **Monitoring & Health Checks** for application reliability

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │     Staging     │    │   Production    │
│   Environment   │    │   Environment   │    │   Environment   │
│    (Port 8000)  │    │   (Port 5001)   │    │   (Port 5002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │      Jenkins CI/CD      │
                    │       Pipeline          │
                    └─────────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │      Docker Registry    │
                    │    & Container Mgmt     │
                    └─────────────────────────┘
```

## 🛠️ Technology Stack

- **Backend Framework:** Flask 2.3.3
- **Testing Framework:** Python unittest, pytest
- **Containerization:** Docker & Docker Compose
- **CI/CD:** Jenkins with declarative pipeline
- **Code Quality:** flake8, pylint, bandit
- **Security:** Safety, container scanning
- **Monitoring:** Health checks, logging
- **Web Server:** Gunicorn (production)

## 📁 Project Structure

```
task-management-system/
├── app.py                 # Main Flask application
├── test_app.py           # Comprehensive unit tests
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── Jenkinsfile          # CI/CD pipeline definition
├── docker-compose.yml   # Multi-service orchestration
├── README.md           # Project documentation
└── logs/               # Application logs directory
```

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Jenkins (for CI/CD)
- Git

### Local Development Setup

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd task-management-system
   ```

2. **Create Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**

   ```bash
   python app.py
   ```

5. **Access Application**
   - Application: http://localhost:8000
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and Run with Docker**

   ```bash
   docker build -t task-management-system .
   docker run -p 8000:8000 task-management-system
   ```

2. **Using Docker Compose**

   ```bash
   # Development environment
   docker-compose up

   # Production environment
   docker-compose --profile production up

   # Testing environment
   docker-compose --profile testing up
   ```

## 🧪 Testing

### Running Unit Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m unittest test_app.py -v

# Run tests with coverage
python -m coverage run -m unittest test_app.py
python -m coverage report -m
python -m coverage html
```

### Test Coverage

The test suite includes 24 comprehensive test cases covering:

- TaskManager class functionality
- Flask API endpoints
- Error handling and edge cases
- Integration testing
- Security validation

## 🔄 CI/CD Pipeline

### Jenkins Pipeline Stages

1. **Checkout** - Clone repository and prepare workspace
2. **Environment Setup** - Configure Python environment
3. **Code Quality & Security Scan** - Lint code and security analysis
4. **Unit Testing** - Execute tests with coverage reporting
5. **Build Docker Image** - Create containerized application
6. **Container Security Scan** - Vulnerability assessment
7. **Integration Testing** - Test containerized application
8. **Push to Registry** - Upload Docker images
9. **Deploy Application** - Deploy to target environment
10. **Smoke Tests** - Verify deployment success

### Pipeline Configuration

The Jenkins pipeline supports:

- **Multi-environment deployment** (dev/staging/production)
- **Parameterized builds** with user-defined options
- **Automated testing** with coverage reporting
- **Security scanning** at multiple stages
- **Notification system** for build status
- **Artifact archiving** for traceability

## 📊 API Documentation

### Endpoints

| Method | Endpoint             | Description        | Request Body                                    |
| ------ | -------------------- | ------------------ | ----------------------------------------------- |
| GET    | `/health`            | Health check       | None                                            |
| GET    | `/tasks`             | Get all tasks      | None                                            |
| POST   | `/tasks`             | Create new task    | `{"title": "string", "description": "string"}`  |
| GET    | `/tasks/{id}`        | Get specific task  | None                                            |
| PUT    | `/tasks/{id}/status` | Update task status | `{"status": "pending\|in_progress\|completed"}` |
| DELETE | `/tasks/{id}`        | Delete task        | None                                            |

### Example Usage

```bash
# Health check
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Complete DevOps Assignment", "description": "Implement CI/CD pipeline"}'

# Get all tasks
curl http://localhost:8000/tasks

# Update task status
curl -X PUT http://localhost:8000/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

## 🔐 Security Features

### Application Security

- Input validation and sanitization
- Error handling without information disclosure
- Non-root container execution
- Minimal container attack surface

### Pipeline Security

- Dependency vulnerability scanning with Safety
- Static code analysis with Bandit
- Container image security scanning
- Secure credential management in Jenkins

## 📈 Monitoring & Logging

### Health Monitoring

- Application health endpoint (`/health`)
- Docker container health checks
- Jenkins pipeline monitoring

### Logging

- Structured application logging
- Container log aggregation
- Build process logging in Jenkins

## 🚢 Deployment Strategies

### Development Environment

- Hot-reload enabled
- Debug mode active
- Direct code mounting

### Staging Environment

- Production-like configuration
- Integration testing environment
- Pre-production validation

### Production Environment

- Optimized container configuration
- Multi-worker Gunicorn setup
- Health checks and restart policies
- Reverse proxy with Nginx

## 🔧 Configuration Management

### Environment Variables

- `FLASK_ENV`: Application environment (development/staging/production)
- `FLASK_DEBUG`: Debug mode toggle
- `PORT`: Application port (default: 8000)

### Docker Configuration

- Multi-stage builds for optimization
- Security-focused base images
- Non-root user execution
- Health check integration

## 📋 Best Practices Implemented

### Development

- **Modular Design**: Separation of concerns with TaskManager class
- **Error Handling**: Comprehensive exception management
- **Documentation**: Inline comments and docstrings
- **Code Quality**: PEP8 compliance and linting

### Testing

- **Test-Driven Development**: Tests written before implementation
- **Comprehensive Coverage**: 24 test cases covering all functionality
- **Integration Testing**: Full API endpoint validation
- **Continuous Testing**: Automated test execution in pipeline

### DevOps

- **Infrastructure as Code**: Dockerfile and docker-compose configuration
- **Pipeline as Code**: Declarative Jenkins pipeline
- **Immutable Infrastructure**: Container-based deployments
- **Security Integration**: Multiple security scanning stages

## 🚀 Scaling Considerations

### Horizontal Scaling

- Stateless application design
- Container orchestration ready
- Load balancer compatible

### Kubernetes Deployment

The application is designed for easy Kubernetes deployment with:

- Stateless architecture
- Health check endpoints
- Configurable environment variables
- Rolling update support

### Performance Optimization

- Gunicorn multi-worker configuration
- Container resource limits
- Efficient Python application structure

## 🔄 Future Enhancements

### Planned Features

- Database integration (PostgreSQL/MySQL)
- User authentication and authorization
- Real-time notifications
- API rate limiting
- Comprehensive metrics collection

### Infrastructure Improvements

- Kubernetes deployment manifests
- Helm charts for package management
- Prometheus monitoring integration
- ELK stack for centralized logging

## 📚 Academic Context

This project demonstrates understanding of:

### Module Learning Outcomes

1. **CI/CD Pipeline Design**: Jenkins automation with multiple stages
2. **Containerization**: Docker best practices and multi-environment support
3. **Testing Strategy**: TDD approach with comprehensive test coverage
4. **Code Quality**: Industry-standard practices and tools
5. **Deployment Automation**: Streamlined release management

### Industry Alignment

- **DevOps Culture**: Collaboration between development and operations
- **Automation**: Reduced manual intervention and human error
- **Quality Assurance**: Multiple validation stages
- **Security Integration**: Shift-left security practices
- **Monitoring**: Observability and reliability focus

## 👥 Contributing

### Development Workflow

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run local quality checks
4. Submit pull request
5. Automated pipeline validation
6. Code review and merge

### Quality Gates

- All tests must pass
- Code coverage > 80%
- Security scans clear
- Code quality standards met

## 📄 License

This project is created for academic purposes as part of the CSY3056 module at the University of Northampton.

## 📞 Support

For questions or issues related to this academic project:

- **Email**: student@university.ac.uk
- **Course**: CSY3056 - Development Operations and Software Testing
- **Institution**: University of Northampton

---

**Note**: This project is designed to demonstrate DevOps best practices and is part of an academic assessment. All configurations and implementations follow industry standards while being suitable for educational evaluation.
