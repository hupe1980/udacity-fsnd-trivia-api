import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = os.environ.get(
            'DATABASE_URL', f'postgresql://caryn@localhost:5432/{self.database_name}')
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIn('questions', data)
        self.assertIn('categories', data)
        self.assertIn('total_questions', data)
        self.assertGreaterEqual(
            data['total_questions'], len(data['questions']))
    
    def test_get_question_with_invalid_page(self):
        res = self.client().get('/questions?page=9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
    
    def test_search_question(self):
        search_term = 'which'
        body = {'searchTerm': search_term }
        res = self.client().post('/questions/search', json=body)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)

    def test_delete_question_with_invalid_id(self):
        res = self.client().delete(f'/questions/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource not found")
        self.assertEqual(data['error'], 404)

    def test_add_question(self):
        body = {
            "question": "Question?",
            "answer": "Answer",
            "category": 1,
            "difficulty": 1
        }
        res = self.client().post('/questions', json=body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
