"""
Author: Uttam Thakur
File Purpose: Unit tests for Task Management System
Dependencies: unittest, Flask
Date: 2025
Description: Comprehensive test suite following TDD principles for the Flask application
"""

import unittest
import json
from app import create_app, TaskManager

class TestTaskManager(unittest.TestCase):
    """Test cases for TaskManager class following TDD approach"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.task_manager = TaskManager()
    
    def tearDown(self):
        """Clean up after each test method"""
        self.task_manager = None
    
    def test_task_manager_initialization(self):
        """Test Case 1: TaskManager initializes correctly"""
        self.assertEqual(len(self.task_manager.tasks), 0)
        self.assertEqual(self.task_manager.task_id_counter, 1)
    
    def test_create_task_success(self):
        """Test Case 2: Create task with valid data"""
        task = self.task_manager.create_task("Test Task", "Test Description")
        
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], "Test Task")
        self.assertEqual(task['description'], "Test Description")
        self.assertEqual(task['status'], 'pending')
        self.assertEqual(task['id'], 1)
        self.assertEqual(len(self.task_manager.tasks), 1)
    
    def test_create_task_empty_title(self):
        """Test Case 3: Create task with empty title should raise ValueError"""
        with self.assertRaises(ValueError):
            self.task_manager.create_task("")
        
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
    """Test cases for Flask application endpoints"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check_endpoint(self):
        """Test Case 13: Health check endpoint returns correct response"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertEqual(data['version'], '1.0.0')
    
    def test_get_tasks_empty(self):
        """Test Case 14: Get tasks when no tasks exist"""
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        
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

    

if __name__ == '__main__':
    # Create test suite
    unittest.main(verbosity=2) 