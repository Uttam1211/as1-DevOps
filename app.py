"""
Author: Uttam Thakur
File Purpose: Main Flask application for Task Management System
Dependencies: Flask, logging
Date: 2025
Description: A modular Flask application demonstrating best practices for DevOps pipeline
"""

from flask import Flask, jsonify, request
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskManager:
    """Task management class following modular design principles"""
    
    def __init__(self):
        self.tasks = []
        self.task_id_counter = 1
        logger.info("TaskManager initialized")
    
    def create_task(self, title, description=""):
        """Create a new task with validation"""
        if not title or not isinstance(title, str):
            raise ValueError("Task title must be a non-empty string")
        
        task = {
            'id': self.task_id_counter,
            'title': title.strip(),
            'description': description.strip(),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        self.task_id_counter += 1
        logger.info(f"Task created with ID: {task['id']}")
        return task
    
    def get_task(self, task_id):
        """Retrieve a task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_all_tasks(self):
        """Retrieve all tasks"""
        return self.tasks
    
    def update_task_status(self, task_id, status):
        """Update task status with validation"""
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        task = self.get_task(task_id)
        if not task:
            return None
        
        task['status'] = status
        task['updated_at'] = datetime.now().isoformat()
        logger.info(f"Task {task_id} status updated to {status}")
        return task
    
    def delete_task(self, task_id):
        """Delete a task by ID"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            logger.info(f"Task {task_id} deleted")
            return True
        return False

def create_app():
    """Application factory pattern for better testability"""
    app = Flask(__name__)
    
    # Initialize task manager
    task_manager = TaskManager()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        """Get all tasks"""
        try:
            tasks = task_manager.get_all_tasks()
            return jsonify({
                'success': True,
                'tasks': tasks,
                'count': len(tasks)
            })
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/tasks', methods=['POST'])
    def create_task():
        """Create a new task"""
        try:
            # Check if content type is JSON
            if not request.is_json:
                return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            title = data.get('title')
            description = data.get('description', '')
            
            task = task_manager.create_task(title, description)
            return jsonify({
                'success': True,
                'task': task
            }), 201
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        """Get a specific task by ID"""
        try:
            task = task_manager.get_task(task_id)
            if not task:
                return jsonify({'success': False, 'error': 'Task not found'}), 404
            
            return jsonify({
                'success': True,
                'task': task
            })
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/tasks/<int:task_id>/status', methods=['PUT'])
    def update_task_status(task_id):
        """Update task status"""
        try:
            data = request.get_json()
            if not data or 'status' not in data:
                return jsonify({'success': False, 'error': 'Status is required'}), 400
            
            task = task_manager.update_task_status(task_id, data['status'])
            if not task:
                return jsonify({'success': False, 'error': 'Task not found'}), 404
            
            return jsonify({
                'success': True,
                'task': task
            })
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """Delete a task"""
        try:
            success = task_manager.delete_task(task_id)
            if not success:
                return jsonify({'success': False, 'error': 'Task not found'}), 404
            
            return jsonify({
                'success': True,
                'message': f'Task {task_id} deleted successfully'
            })
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 