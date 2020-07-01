# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# ----------------------------------------------------------------------------#
# Helper Functions
# ----------------------------------------------------------------------------#


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # ----------------------------------------------------------------------#
    # App Configuration
    # ----------------------------------------------------------------------#
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS"
        )

        return response

    # ----------------------------------------------------------------------#
    # Retrieve Categories
    # ----------------------------------------------------------------------#

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)
        return jsonify(
            {"categories": {category.id: category.type for category in categories}}
        )

    # ----------------------------------------------------------------------#
    # Retrieve Questions
    # ----------------------------------------------------------------------#

    @app.route("/questions", methods=["GET"])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)
        return jsonify(
            {
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category": None,
                "categories": {category.id: category.type for category in categories},
            }
        )

    # ----------------------------------------------------------------------#
    # Delete Questions
    # ----------------------------------------------------------------------#

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.order_by(Category.id).all()

            if len(current_questions) == 0:
                abort(404)
            return jsonify(
                {
                    "success": True,
                    "deleted_id": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": None,
                    "categories": {
                        category.id: category.type for category in categories
                    },
                }
            )
        except Exception as e:
            print(e)
            abort(422)

    # ----------------------------------------------------------------------#
    # Create Questions
    # ----------------------------------------------------------------------#

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.order_by(Category.id).all()

            return jsonify(
                {
                    "success": True,
                    "created_id": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": None,
                    "categories": {
                        category.id: category.type for category in categories
                    },
                }
            )
        except Exception as e:
            print(e)
            abort(422)

    # ----------------------------------------------------------------------#
    # Search Questions
    # ----------------------------------------------------------------------#

    @app.route("/questions-search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)
        categories = Category.query.order_by(Category.id).all()

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike("%{}%".format(search_term))
            )
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "questions": current_questions,
                    "total_questions": len(selection.all()),
                    "current_category": None,
                    "categories": {
                        category.id: category.type for category in categories
                    },
                }
            )
        except Exception as e:
            print(e)
            abort(422)

    # ----------------------------------------------------------------------#
    # Get Questions Based on Category
    # ----------------------------------------------------------------------#

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        selection = Question.query.filter(Question.category == category_id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)
        return jsonify(
            {
                "questions": current_questions,
                "total_questions": len(selection),
                "current_category": category_id,
                "categories": {category.id: category.type for category in categories},
            }
        )

    # ----------------------------------------------------------------------#
    # Retrieve Question to Play Quiz
    # ----------------------------------------------------------------------#

    @app.route("/quizzes", methods=["POST"])
    def get_quiz_questions():
        body = request.get_json()
        previous_questions = body.get("previous_questions", [])
        quiz_category = body.get("quiz_category", None)

        try:
            if quiz_category:
                if quiz_category["id"] == 0:
                    questions = Question.query.all()
                else:
                    questions = Question.query.filter(
                        Question.category == quiz_category["id"]
                    ).all()
            if not questions:
                return abort(422)
            question_options = []
            for question in questions:
                if question.id not in previous_questions:
                    question_options.append(question.format())
            if len(question_options) != 0:
                next_question = random.choice(question_options)
                return jsonify({"question": next_question})
            else:
                return jsonify({"question": False})

        except Exception as e:
            print(e)
            abort(422)

    # ----------------------------------------------------------------------#
    # Error Handlers
    # ----------------------------------------------------------------------#

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "bad request - server cannot process the request",
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "internal service error"}
            ),
            500,
        )

    return app
