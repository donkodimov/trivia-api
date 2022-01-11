import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from sqlalchemy.sql.expression import true

from sqlalchemy.sql.functions import current_date
from flask_wtf import FlaskForm as Form
from forms import *


from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/questions")
    def get_requests():

        try:
            selection1 = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection1)

            current_category = Category.query.get(1)
            categories = {x.id: x.type for x in Category.query.all()}

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "questions": current_questions,
                    "total_questions": len(selection1),
                    "categories": categories,
                    "currentCategory": current_category.type,
                }
            )
        except ValueError as e:
            print(e)

    @app.route("/categories")
    def get_categories():

        try:
            categories = {x.id: x.type for x in Category.query.all()}

            if len(categories) == 0:
                abort(404)

            return jsonify({"categories": categories})
        except ValueError as e:
            print(e)

    @app.route("/categories/<int:cat_id>/questions")
    def get_questions_for_category(cat_id):

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.category == str(cat_id)
            )

            current_category = Category.query.get(cat_id)
            current_questions = paginate_questions(request, selection)
            categories = {x.id: x.type for x in Category.query.all()}

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "questions": current_questions,
                    "totalQuestions": len(current_questions),
                    "currentCategory": current_category.type,
                }
            )
        except ValueError as e:
            print(e)

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        question = Question.query.filter(Question.id == id).one_or_none()
        if question is None:
            abort(404)
        else:
            question.delete()
            return jsonify(
                {"success": True, "id": question.id, "message": "Question deleted"}
            )

    @app.route("/questions", methods=["POST"])
    def add_question():
        form = AddForm()
        print(form)
        search_term = request.form.get("search_term", "")
        print(search_term)

        try:

            for i in [
                form.question.data,
                form.answer.data,
                form.difficulty.data,
                form.category.data,
            ]:
                if not i:
                    abort(422)

            question = Question(
                question=form.question.data,
                answer=form.answer.data,
                difficulty=form.difficulty.data,
                category=form.category.data,
            )
            question.insert()

            return jsonify({"success": True, "id": question.id})
        except ValueError as e:
            print(e)

    @app.route("/questions/search", methods=["POST"])
    def search_question():
        data = SearchForm()
        print(data.searchTerm.data)

        try:
            if not data.searchTerm.data:
                abort(422)

            selection = Question.query.filter(
                Question.question.ilike("%" + data.searchTerm.data + "%")
            )
            if not selection.all():
                abort(404)
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": len(selection.all()),
                }
            )

        except ValueError as e:
            print(e)

    @app.route("/quizzes", methods=["POST"])
    def start_quiz():
        body = request.get_json()
        previous_questions = body.get("previous_questions", [])
        quiz_category = body["quiz_category"]["id"]
        if quiz_category == 0:
            all_questions = Question.query.all()
        else:
            all_questions = Question.query.filter(Question.category == quiz_category)

        try:
            random_question_id = random.choice(
                [x.id for x in all_questions if x.id not in previous_questions]
            )
        except IndexError as e:
            print(e)
            print("All questions tried for this category")
            abort(422)

        result = Question.query.filter(Question.id == random_question_id).one()
        print([x.id for x in all_questions if x.id not in previous_questions])

        return jsonify({"success": True, "question": result.format()})

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource Not Found"}),
            404,
        )

    @app.errorhandler(405)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Not Processable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Bad Request"}),
            400,
        )

    return app
