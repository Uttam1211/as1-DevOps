"""
Task Management System - Test Suite
---------------------------------

A comprehensive test suite for the Task Management System implementing industry-standard
testing practices and patterns.

Author: Uttam Thakur
Version: 1.0.0
License: MIT
Created: 2025
Updated: 2025

This module provides:
- Unit tests for TaskManager class
- Integration tests for Flask endpoints
- Edge case coverage
- Error condition validation
"""

import unittest
import json
from typing import Optional, Dict, Any
from http import HTTPStatus
from datetime import datetime

from app import create_app, TaskManager

class TestTaskManager(unittest.TestCase):
    """
    Unit test suite for TaskManager class.
    
    This test suite verifies the core business logic of the TaskManager class,
    including CRUD operations, validation, and error handling.
    
    Test Categories:
    - Initialization
    - Task Creation
    - Task Retrieval
    - Task Updates
    - Task Deletion
    - Error Handling
    """
    
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates a fresh TaskManager instance for each test to ensure
        test isolation and prevent state interference.
        """
        self.task_manager = TaskManager()
    
    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.
        
        Ensures proper cleanup of resources and prevents state leakage
        between tests.
        """
        self.task_manager = None
    
    def test_task_manager_initialization(self) -> None:
        """
        Verify TaskManager initializes with correct default state.
        
        Ensures:
        - Empty task list
        - Counter starts at 1
        - No residual state
        """
        self.assertEqual(len(self.task_manager.tasks), 0)
        self.assertEqual(self.task_manager.task_id_counter, 1)
    
    def test_create_task_success(self) -> None:
        """
        Verify successful task creation with valid data.
        
        Tests:
        - Task creation with title and description
        - Correct ID assignment
        - Default status
        - Timestamp presence
        """
        task = self.task_manager.create_task("Test Task", "Test Description")
        
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], "Test Task")
        self.assertEqual(task['description'], "Test Description")
        self.assertEqual(task['status'], 'pending')
        self.assertEqual(task['id'], 1)
        self.assertEqual(len(self.task_manager.tasks), 1)
        self.assertIn('created_at', task)
        self.assertIn('updated_at', task)
    
    def test_create_task_empty_title(self) -> None:
        """
        Verify task creation fails with empty or None title.
        
        Tests:
        - Empty string title
        - None title
        - Error message clarity
        """
        with self.assertRaises(ValueError) as context:
            self.task_manager.create_task("")
        self.assertIn("non-empty string", str(context.exception))
        
        with self.assertRaises(ValueError):
            self.task_manager.create_task(None)
    
    def test_create_task_invalid_title_type(self):
        """Test Case 4: Create task with non-string title should raise ValueError"""
        with self.assertRaises(ValueError):
            self.task_manager.create_task(123)
        
        with self.assertRaises(ValueError):
            self.task_manager.create_task([])
    
    def test_get_task_success(self):
        """Test Case 5: Retrieve existing task by ID"""
        created_task = self.task_manager.create_task("Test Task")
        retrieved_task = self.task_manager.get_task(1)
        
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task['id'], 1)
        self.assertEqual(retrieved_task['title'], "Test Task")
    
    def test_get_task_not_found(self):
        """Test Case 6: Retrieve non-existing task returns None"""
        task = self.task_manager.get_task(999)
        self.assertIsNone(task)
    
    def test_get_all_tasks(self):
        """Test Case 7: Retrieve all tasks"""
        self.task_manager.create_task("Task 1")
        self.task_manager.create_task("Task 2")
        
        all_tasks = self.task_manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 2)
        self.assertEqual(all_tasks[0]['title'], "Task 1")
        self.assertEqual(all_tasks[1]['title'], "Task 2")
    
    def test_update_task_status_success(self):
        """Test Case 8: Update task status with valid status"""
        self.task_manager.create_task("Test Task")
        updated_task = self.task_manager.update_task_status(1, 'completed')
        
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task['status'], 'completed')
    
    def test_update_task_status_invalid_status(self):
        """Test Case 9: Update task with invalid status should raise ValueError"""
        self.task_manager.create_task("Test Task")
        
        with self.assertRaises(ValueError):
            self.task_manager.update_task_status(1, 'invalid_status')
    
    def test_update_task_status_not_found(self):
        """Test Case 10: Update non-existing task returns None"""
        result = self.task_manager.update_task_status(999, 'completed')
        self.assertIsNone(result)
    
    def test_delete_task_success(self):
        """Test Case 11: Delete existing task"""
        self.task_manager.create_task("Test Task")
        result = self.task_manager.delete_task(1)
        
        self.assertTrue(result)
        self.assertEqual(len(self.task_manager.tasks), 0)
    
    def test_delete_task_not_found(self):
        """Test Case 12: Delete non-existing task returns False"""
        result = self.task_manager.delete_task(999)
        self.assertFalse(result)

class TestFlaskApp(unittest.TestCase):
    """
    Integration test suite for Flask application endpoints.
    
    This test suite verifies the REST API endpoints, including:
    - Request/response cycle
    - Status codes
    - Response formats
    - Error handling
    - Edge cases
    """
    
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates:
        - Test Flask application
        - Test client
        - Configures test environment
        """
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.base_url = '/tasks'
    
    def create_test_task(self, title: str = "Test Task", description: str = "") -> Dict[str, Any]:
        """
        Helper method to create a test task.
        
        Args:
            title: Task title (default: "Test Task")
            description: Task description (default: "")
            
        Returns:
            Dict containing the created task data
        """
        task_data = {
            'title': title,
            'description': description
        }
        response = self.client.post(
            self.base_url,
            data=json.dumps(task_data),
            content_type='application/json'
        )
        return json.loads(response.data)
    
    def test_health_check_endpoint(self) -> None:
        """
        Verify health check endpoint functionality.
        
        Ensures:
        - 200 status code
        - Correct response format
        - Required fields present
        - Version information
        """
        response = self.client.get('/health')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertEqual(data['version'], '1.0.0')
        self.assertIn('environment', data)
    
    def test_get_tasks_empty(self) -> None:
        """
        Verify get tasks endpoint with empty task list.
        
        Ensures:
        - 200 status code
        - Empty task list
        - Correct count
        - Success indicator
        """
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['tasks']), 0)
    
    def test_create_task_success(self):
        """Test Case 15: Create task via API with valid data"""
        task_data = {
            'title': 'Test API Task',
            'description': 'Test description'
        }
        
        response = self.client.post('/tasks',
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['task']['title'], 'Test API Task')
    
    def test_create_task_no_data(self):
        """Test Case 16: Create task with no JSON data"""
        response = self.client.post('/tasks')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_create_task_empty_title(self):
        """Test Case 17: Create task with empty title via API"""
        task_data = {'title': ''}
        
        response = self.client.post('/tasks',
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_get_specific_task_success(self):
        """Test Case 18: Get specific task by ID via API"""
        # First create a task
        task_data = {'title': 'Test Task'}
        self.client.post('/tasks',
                        data=json.dumps(task_data),
                        content_type='application/json')
        
        # Then retrieve it
        response = self.client.get('/tasks/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['task']['id'], 1)
    
    def test_get_specific_task_not_found(self):
        """Test Case 19: Get non-existing task by ID"""
        response = self.client.get('/tasks/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_update_task_status_success(self):
        """Test Case 20: Update task status via API"""
        # First create a task
        task_data = {'title': 'Test Task'}
        self.client.post('/tasks',
                        data=json.dumps(task_data),
                        content_type='application/json')
        
        # Then update its status
        update_data = {'status': 'completed'}
        response = self.client.put('/tasks/1/status',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['task']['status'], 'completed')
    
    def test_update_task_status_invalid(self):
        """Test Case 21: Update task with invalid status"""
        # First create a task
        task_data = {'title': 'Test Task'}
        self.client.post('/tasks',
                        data=json.dumps(task_data),
                        content_type='application/json')
        
        # Then try to update with invalid status
        update_data = {'status': 'invalid_status'}
        response = self.client.put('/tasks/1/status',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_delete_task_success(self):
        """Test Case 22: Delete task via API"""
        # First create a task
        task_data = {'title': 'Test Task'}
        self.client.post('/tasks',
                        data=json.dumps(task_data),
                        content_type='application/json')
        
        # Then delete it
        response = self.client.delete('/tasks/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_delete_task_not_found(self):
        """Test Case 23: Delete non-existing task"""
        response = self.client.delete('/tasks/999')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_invalid_endpoint(self):
        """Test Case 24: Access invalid endpoint returns 404"""
        response = self.client.get('/invalid-endpoint')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    def test_create_task_validation(self) -> None:
        """
        Verify task creation input validation.
        
        Tests:
        - Missing title
        - Empty title
        - Invalid content type
        - Missing request body
        """
        # Test missing title
        response = self.client.post(
            self.base_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        
        # Test empty title
        response = self.client.post(
            self.base_url,
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        
        # Test invalid content type
        response = self.client.post(
            self.base_url,
            data='not json'
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    def test_task_lifecycle(self) -> None:
        """
        Verify complete task lifecycle through API.
        
        Tests sequence:
        1. Create task
        2. Retrieve task
        3. Update task status
        4. Delete task
        5. Verify deletion
        """
        # Create task
        create_response = self.create_test_task()
        self.assertEqual(create_response['task']['status'], 'pending')
        task_id = create_response['task']['id']
        
        # Update status
        update_response = self.client.put(
            f'{self.base_url}/{task_id}/status',
            data=json.dumps({'status': 'completed'}),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, HTTPStatus.OK)
        
        # Delete task
        delete_response = self.client.delete(f'{self.base_url}/{task_id}')
        self.assertEqual(delete_response.status_code, HTTPStatus.OK)
        
        # Verify deletion
        get_response = self.client.get(f'{self.base_url}/{task_id}')
        self.assertEqual(get_response.status_code, HTTPStatus.NOT_FOUND)

if __name__ == '__main__':
    unittest.main(verbosity=2) 