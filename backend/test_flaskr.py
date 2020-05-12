# Note to user: Prior to running this script, you will want 
#      to set the postgresql password to 'udacity' in your 
#      environemnt, by typing either 'set PGPASSWORD=udacity' 
#      (for Windows) or 'export PGPASSWORD=udacity' (for n
#      on-Windows) in your command line.  If you do not set 
#      this variable in the  environment then you will have 
#      to answer udacity as the password 2-3 times during the 
#      db drop/create/populate process

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
        self.database_user = 'udacity'
        self.database_password = 'udacity'
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_user, self.database_password, 'localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_a_get_categories_success(self):
      '''Test /categories GET endpoint with properly formed request '''
      res = self.client().get('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
    
    def test_b_get_categories_fail(self):
      '''Test /categories GET endpoint with improper request'''
      res = self.client().post('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 405)
      self.assertFalse(data['success'])

    def test_c_get_questions_success(self):
      ''' Test /questions GET endpoint with properly formed request '''
      res = self.client().get('/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertEqual(len(data['questions']), 10)
      self.assertEqual(data['total_questions'], 19)

    def test_d_get_questions_fail(self):
      ''' Test /questions GET endpoint with improper request ('page' out of bounds) '''
      res = self.client().get('/questions&page=4')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])
      self.assertEqual(data['error'], 404)
    
    def test_e_delete_question_success(self):
      ''' Test questions/<id> DELETE endpoint with properly formed request to delete a question '''
      res = self.client().delete('/questions/5')
      data = json.loads(res.data)
      total_questions = len(Question.query.all())
      deleted_question = Question.query.get(5)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertIsNone(deleted_question)
      self.assertEqual(total_questions, 18)

    def test_f_delete_question_fail(self):
      ''' Test /questions/<id> DELETE endpoint with improper request (id for nonexistent question) '''
      res = self.client().delete('/questions/73')
      data = json.loads(res.data)
      total_questions = len(Question.query.all())

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])
      self.assertEqual(total_questions, 18)
    
    def test_g_add_question_success(self):
      ''' Test add question functionality of /questions POST endpoint with properly formed request to add a new question '''
      new_question = {
        'question': 'What is the air-speed velocity of an unladen swallow?',
        'answer': 'What do you mean? An African or European swallow?',
        'difficulty': 5,
        'category': 5
      }

      res = self.client().post('/questions', json=new_question, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      total_questions = len(Question.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(total_questions, 19)
    
    def test_h_add_question_fail(self):
      ''' Test add question functionality of /questions POST endpoint with improperly formed request to add a new question (no actual text supplied for new question) '''
      new_question = {
        'question': '',
        'answer': 'What do you mean? An African or European swallow?',
        'difficulty': 5,
        'category': 5
      }

      res = self.client().post('/questions', json=new_question, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      total_questions = len(Question.query.all())

      self.assertEqual(res.status_code, 422)
      self.assertFalse(data['success'])
      self.assertEqual(total_questions, 19)
  
    def test_i_search_success_w_results(self):
      ''' Test search functionality of /questions POST endpoint with property formed search request that should retrieve 2 results '''
      res = self.client().post('/questions', json={'searchTerm': 'sOcCe'}, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      question_ids = sorted([question['id'] for question in data['questions']])

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(data['total_questions'], 2)
      self.assertEqual(question_ids, [10, 11])

    def test_j_search_success_no_results(self):
      ''' Test search functionality of /questions POST endpoint with properly formed search request for term that should have no results in test database '''
      res = self.client().post('/questions', json={'searchTerm': 'Smashmouth'}, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(data['total_questions'], 0)
    
    def test_k_search_fail(self):
      ''' Test search functionality of /questions POST endpoint with improper request (no data supplied in json request body) '''
      res = self.client().post('/questions', json={}, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertFalse(data['success'])

    def test_l_category_search_success(self):
      ''' Test search functionality of /categories/<id>/questions GET endpoint with properly form search request'''
      res = self.client().get('/categories/3/questions')
      data = json.loads(res.data)
      num_returned_questions = len(data['questions'])
      question_ids = sorted([question['id'] for question in data['questions']])

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertEqual(num_returned_questions, 3)
      self.assertEqual(data['total_questions'], 3)
      self.assertEqual(question_ids, [13, 14, 15])
    
    def test_m_category_search_fail(self):
      ''' Test search functionality of /categories/<id>/questions GET endpoint with improperly form search request'''
      res = self.client().get('/categories/7/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])

    def test_n_start_quiz_in_cat_success(self):
      ''' Test /quizzes POST endpoint with properly formatted request for question in specific category'''
      res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 1} })
      data = json.loads(res.data)
      
      question_id = data['question']['id']

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertIn(question_id, [20, 21, 22])

    def test_o_start_quiz_in_all_success(self):
      ''' Test /quizzes POST endpoint with properly formatted request for question with ALL categories selected'''
      res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 0} })
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertTrue(data['question'])
    
    def test_p_start_quiz_in_cat_out_of_questions(self):
      ''' Test /quizzes POST endpoint with properly formatted request for question in category where all questions have been exhausted'''
      res = self.client().post('/quizzes', json={'previous_questions': [13, 14, 15], 'quiz_category': {'id': 3} })
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['success'])
      self.assertNotIn('question', data.keys())

    def test_q_start_quiz_fail(self):
      ''' Test /quizzes POST endpoint with improperly formatted request for question (category does not exist)'''
      res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 9} })
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    os.system('dropdb -U udacity trivia_test')
    os.system('createdb -U udacity trivia_test')
    os.system('psql -U udacity trivia_test < trivia.psql')

    unittest.main()