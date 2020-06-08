import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:root@localhost:5432/trivia'
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Name the two holy cities of Saudi Arabia',
            'answer': 'Mecca, Almadenah Almonawara',
            'difficulty': 3,
            'category': '3'
        }

    def tearDown(self):
        pass

    def test_get_paginated_questions(self):

        res = self.client().get('/questions')
        data = json.loads(res.data)

        # check status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that total_questions
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_request_beyond_valid_page(self):

        # request unexist page
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        # check status code
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        # will add a question and delete it later
        addition_response = self.client().post(
                    '/questions', json=self.new_question)
        # get the response after addtion
        addition_data = json.loads(addition_response.data)
        # delete the question we just added it
        deletion_response = self.client().delete(
            '/questions/{}'.format(addition_data['created']))
        deletion_data = json.loads(deletion_response.data)
        questions_after = Question.query.all()
        question = Question.query.filter(
            Question.id == addition_data['created']).one_or_none()

        self.assertEqual(deletion_response.status_code, 200)
        self.assertEqual(deletion_data['success'], True)
        self.assertEqual(deletion_data['deleted'], addition_data['created'])
        self.assertTrue(
            addition_data['total_questions'] > len(questions_after))
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        # select an question to delete
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_question(self):
        # query all questions before insertion
        questions_before_newquestion = Question.query.all()

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        # query all questions after insertion
        questions_After_newquestion = Question.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # if number of  questions is incresing mean we have successfull
        # insertion
        self.assertTrue(len(questions_before_newquestion)
                        < len(questions_After_newquestion))

    def test_422_if_question_creation_not_allowed(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        """Tests search questions success"""

        # send post request with search term
        res = self.client().post('/search',
                                 json={'searchTerm': 'play'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_404_if_search_questions_fails(self):
        """Tests search questions failure 404"""

        # enter word does not existin adtabase to test failure
        response = self.client().post('/search',
                                      json={'searchTerm': 'hvjvjvjvj'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):

        res = self.client().get('/categories/4/questions')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'History')

    def test_404_if_questions_by_category_fails(self):
        # request questions with category 600
        res = self.client().get('/categories/600/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_random_quiz_question(self):

        res = self.client().post(
            '/quizzes',
            json={
                'previous_questions': [
                    13,
                    14],
                'quiz_category': {
                    'type': 'Geography',
                    'id': '3'}})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 3)
        self.assertNotEqual(data['question']['id'], 10)
        self.assertNotEqual(data['question']['id'], 11)

        def test_random_quiz_question_fails(self):

            res = self.client().post('/quizzes', json={})

            data = json.loads(res.data)

            self.assertEqual(res.status_code, 400)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
