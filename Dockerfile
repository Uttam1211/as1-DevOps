# Dockerfile for Task Management System
# Author: Uttam Thakur
# Purpose: Containerize Flask application for consistent deployment
# Date: 2025
# Base Image: Python 3.11 slim for security and efficiency

# Use official Python runtime as base image
FROM python:3.11-slim

# Set metadata labels for better container management
LABEL maintainer="uttam1thakur@gmail.com"
LABEL version="1.0.0"
LABEL description="Task Management System Flask Application"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=8000

# Create non-root user for security
RUN groupadd -r flaskgroup && useradd -r -g flaskgroup flaskuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY test_app.py .

# Create logs directory and set permissions
RUN mkdir -p /app/logs \
    && chown -R flaskuser:flaskgroup /app \
    && chmod -R 755 /app

# Switch to non-root user
USER flaskuser

# Health check to ensure container is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# For university project - use simple Python command for easier debugging
CMD ["python3", "-u", "app.py"] 