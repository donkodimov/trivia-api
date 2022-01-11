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
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["currentCategory"])
        self.assertEqual(len(data["questions"]), 10)

    def test_404_paginated_questions(self):
        Question.query.delete()
        res = self.client().get("/questions?page=333")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_get_questions_empty_db(self):
        Question.query.delete()
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertEqual(len(data["categories"]), 6)

    def test_404_get_categories(self):
        Category.query.delete()
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")
    
    def test_get_questions_for_cateogry(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertEqual(data["currentCategory"], "Science")

    def test_404_questions_for_cateogry(self):
        Question.query.filter(Question.category == 1).delete()
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_405_questions_for_cateogry(self):
        res = self.client().post("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    def test_delete_questions(self):
        # This test will success only once on a fresh db. Comment out after.
        res = self.client().delete("/questions/19")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["id"], 19)

    def test_404_delete_questions(self):
        res = self.client().delete("/questions/10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_add_question(self):
        res = self.client().post("/questions", json={"question": "Add question",
                                                     "answer": "Add answer",
                                                     "difficulty": 4,
                                                     "category": '1'})
        data = json.loads(res.data)

        query = Question.query.filter(Question.answer == 'Add answer').first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(query.answer.format(), 'Add answer')

    def test_422_add_question(self):
        res = self.client().post("/questions", json={"question": "empty answer",
                                                     "answer": "",
                                                     "difficulty": 4,
                                                     "category": '1'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Processable")

    def test_search_question(self):
        res = self.client().post("/questions/search", json={"searchTerm": "Add question"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])


    def test_404_search_question(self):
        res = self.client().post("/questions/search", json={"searchTerm": "not existing"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_quizzes(self):
        request_body = {
                        "previous_questions": [1, 4, 14, 16],
                        "quiz_category": {
                                            "type": "Science", 
                                            "id": "2"
                                         }
                        }
        res = self.client().post("/quizzes", json=request_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_422_quizzes(self):
        request_body = {
                        "previous_questions": [13, 14, 15],
                        "quiz_category": {
                                            "type": "Geography", 
                                            "id": "3"
                                         }
                        }
        res = self.client().post("/quizzes", json=request_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Processable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()