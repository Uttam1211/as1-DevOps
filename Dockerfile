# =============================================================================
# Task Management System - Dockerfile
# Author: Uttam Thakur
# Course: CSY3056 - DevOps
# University of Northampton
#
# Purpose: This Dockerfile creates a production-ready container for the Flask
# application with proper security measures and optimizations.
# =============================================================================

# Base Image Selection
# Using slim variant for reduced attack surface and smaller image size
FROM python:3.11-slim

# Container Metadata
# Provides essential information for container management and documentation
LABEL maintainer="uttam1thakur@gmail.com" \
      version="1.0.0" \
      description="Task Management System - Production Container"

# Environment Configuration
# Critical application settings and Python behavior modifications
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=8000

# Security Configuration
# Create non-root user for enhanced security
RUN groupadd -r flaskgroup && useradd -r -g flaskgroup flaskuser

# Application Directory Setup
WORKDIR /app

# System Dependencies
# Install only necessary system packages for minimal container size
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Application Dependencies
# Copy and install Python packages first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Application Code
# Copy application files after installing dependencies
COPY app.py .
COPY test_app.py .

# Directory and Permission Setup
# Create necessary directories and set appropriate permissions
RUN mkdir -p /app/logs \
    && chown -R flaskuser:flaskgroup /app \
    && chmod -R 755 /app

# Security Measure
# Switch to non-root user for running the application
USER flaskuser

# Container Health Monitoring
# Regular health checks to ensure application availability
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Network Configuration
EXPOSE ${PORT}

# Application Startup
# Using Python's unbuffered mode for proper logging in containers
CMD ["python3", "-u", "app.py"] 