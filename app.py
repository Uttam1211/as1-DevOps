"""
Task Management System
---------------------

A RESTful Flask application implementing a task management system with industry-standard practices.

Author: Uttam Thakur
Version: 1.0.0
License: MIT
Created: 2025   
Updated: 2025

This module implements a production-ready Flask application with:
- Comprehensive error handling
- Input validation
- Logging configuration
- Health monitoring
- RESTful API endpoints
- Modular design patterns
"""

from flask import Flask, jsonify, request
from datetime import datetime
import logging
import os
from typing import Dict, List, Optional, Union
from http import HTTPStatus

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Type aliases for better code readability
TaskType = Dict[str, Union[int, str]]
TaskListType = List[TaskType]

class TaskManager:
    """
    Task Management System core logic implementation.
    
    This class handles all task-related operations including CRUD operations
    and status management. It implements validation and logging for all operations.
    
    Attributes:
        tasks (List[Dict]): List storing all tasks
        task_id_counter (int): Auto-incrementing counter for task IDs
    """
    
    VALID_STATUSES = ['pending', 'in_progress', 'completed']
    
    def __init__(self) -> None:
        """Initialize TaskManager with empty task list."""
        self.tasks: TaskListType = []
        self.task_id_counter: int = 1
        logger.info("TaskManager initialized successfully")
    
    def create_task(self, title: str, description: str = "") -> TaskType:
        """
        Create a new task with validation.
        
        Args:
            title: Task title (required)
            description: Task description (optional)
            
        Returns:
            Dict containing the created task
            
        Raises:
            ValueError: If title is empty or invalid
        """
        if not title or not isinstance(title, str):
            logger.error("Invalid task title provided")
            raise ValueError("Task title must be a non-empty string")
        
        task: TaskType = {
            'id': self.task_id_counter,
            'title': title.strip(),
            'description': description.strip(),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        self.task_id_counter += 1
        logger.info(f"Task created successfully with ID: {task['id']}")
        return task
    
    def get_task(self, task_id: int) -> Optional[TaskType]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: Unique identifier of the task
            
        Returns:
            Task dictionary if found, None otherwise
        """
        task = next((task for task in self.tasks if task['id'] == task_id), None)
        if task:
            logger.debug(f"Task retrieved: ID {task_id}")
        else:
            logger.debug(f"Task not found: ID {task_id}")
        return task
    
    def get_all_tasks(self) -> TaskListType:
        """
        Retrieve all tasks.
        
        Returns:
            List of all tasks
        """
        logger.debug(f"Returning all tasks. Count: {len(self.tasks)}")
        return self.tasks
    
    def update_task_status(self, task_id: int, status: str) -> Optional[TaskType]:
        """
        Update task status with validation.
        
        Args:
            task_id: Unique identifier of the task
            status: New status value
            
        Returns:
            Updated task dictionary if found, None otherwise
            
        Raises:
            ValueError: If status is invalid
        """
        if status not in self.VALID_STATUSES:
            logger.error(f"Invalid status provided: {status}")
            raise ValueError(f"Status must be one of: {self.VALID_STATUSES}")
        
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Attempt to update non-existent task: ID {task_id}")
            return None
        
        task['status'] = status
        task['updated_at'] = datetime.now().isoformat()
        logger.info(f"Task {task_id} status updated to {status}")
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: Unique identifier of the task
            
        Returns:
            bool: True if task was deleted, False if not found
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            logger.info(f"Task {task_id} deleted successfully")
            return True
        logger.warning(f"Attempt to delete non-existent task: ID {task_id}")
        return False

def create_app() -> Flask:
    """
    Application factory function.
    
    Creates and configures the Flask application using the factory pattern.
    This pattern is preferred for better testability and configuration management.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    task_manager = TaskManager()
    
    @app.route('/health', methods=['GET'])
    def health_check() -> tuple[dict, int]:
        """
        Health check endpoint for monitoring.
        
        Returns:
            Tuple of (response_data, status_code)
        """
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'production')
        }), HTTPStatus.OK
    
    @app.route('/tasks', methods=['GET'])
    def get_tasks() -> tuple[dict, int]:
        """
        Get all tasks endpoint.
        
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            tasks = task_manager.get_all_tasks()
            return jsonify({
                'success': True,
                'tasks': tasks,
                'count': len(tasks)
            }), HTTPStatus.OK
        except Exception as e:
            logger.exception("Error retrieving tasks")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.route('/tasks', methods=['POST'])
    def create_task() -> tuple[dict, int]:
        """
        Create new task endpoint.
        
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type must be application/json'
                }), HTTPStatus.BAD_REQUEST
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), HTTPStatus.BAD_REQUEST
            
            title = data.get('title')
            description = data.get('description', '')
            
            task = task_manager.create_task(title, description)
            return jsonify({
                'success': True,
                'task': task
            }), HTTPStatus.CREATED
        
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), HTTPStatus.BAD_REQUEST
        except Exception as e:
            logger.exception("Error creating task")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id: int) -> tuple[dict, int]:
        """
        Get specific task endpoint.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            task = task_manager.get_task(task_id)
            if not task:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), HTTPStatus.NOT_FOUND
            
            return jsonify({
                'success': True,
                'task': task
            }), HTTPStatus.OK
        except Exception as e:
            logger.exception(f"Error retrieving task {task_id}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.route('/tasks/<int:task_id>/status', methods=['PUT'])
    def update_task_status(task_id: int) -> tuple[dict, int]:
        """
        Update task status endpoint.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            data = request.get_json()
            if not data or 'status' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Status is required'
                }), HTTPStatus.BAD_REQUEST
            
            task = task_manager.update_task_status(task_id, data['status'])
            if not task:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), HTTPStatus.NOT_FOUND
            
            return jsonify({
                'success': True,
                'task': task
            }), HTTPStatus.OK
        
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), HTTPStatus.BAD_REQUEST
        except Exception as e:
            logger.exception(f"Error updating task {task_id}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id: int) -> tuple[dict, int]:
        """
        Delete task endpoint.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            success = task_manager.delete_task(task_id)
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), HTTPStatus.NOT_FOUND
            
            return jsonify({
                'success': True,
                'message': f'Task {task_id} deleted successfully'
            }), HTTPStatus.OK
        except Exception as e:
            logger.exception(f"Error deleting task {task_id}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.errorhandler(404)
    def not_found(error) -> tuple[dict, int]:
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), HTTPStatus.NOT_FOUND
    
    @app.errorhandler(500)
    def internal_error(error) -> tuple[dict, int]:
        """Handle 500 errors."""
        logger.exception("Internal server error occurred")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    return app

if __name__ == '__main__':
    # Get port from environment variable with fallback to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # Create and run application
    app = create_app()
    
    # Production-ready configuration
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    ) 