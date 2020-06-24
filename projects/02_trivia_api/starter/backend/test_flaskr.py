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
        self.database_path = "postgres://{}/{}".format(
            "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Located in Cambodia, what is the largest religious monument in the world?",
            "answer": "Angkor Wat",
            "category": 3,
            "difficulty": 3,
        }

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

    def test_get_paginated_questions(self):
        """ Test if questions can be retrieved """
        response = self.client().get("/questions")
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertIsNone(data["current_category"])
        self.assertTrue(len(data["categories"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        """ Test if 404 error when the page is invalid """
        response = self.client().get("/questions?page=1000")
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_categories(self):
        """ Test if categories can be retrieved """
        response = self.client().get("/categories")
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data["categories"]))

    def test_delete_question(self):
        """ Test if a given question can be deleted """
        response = self.client().delete("/questions/4")
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 4).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted_id"], 4)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertIsNone(data["current_category"])
        self.assertTrue(len(data["categories"]))

    def test_422_if_question_does_not_exist(self):
        """ Test if 422 error when question id is invalid """
        response = self.client().delete("/questions/10000")
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_new_question(self):
        """ Test if a new question can be created and added to the db """
        response = self.client().post("/questions", json=self.new_question)
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created_id"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertIsNone(data["current_category"])
        self.assertTrue(len(data["categories"]))

    def test_405_if_question_creation_not_allowed(self):
        """ Test if 405 error when method is invalid """
        response = self.client().post("/questions/45", json=self.new_question)
        self.assertTrue(is_json(response.data), "invalid JSON")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")


# check if string is JSON
def is_json(data):
    try:
        json.loads(data)
    except ValueError as e:
        return False
    return True


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
