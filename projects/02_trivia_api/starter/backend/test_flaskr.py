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
