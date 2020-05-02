import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        return response

    # Helper function to paginate questions
    def paginate_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        current_question = [question.format()
                            for question in questions[start:end]]

        return current_question

    @app.route('/categories', methods=['GET'])
    def get_categories():
        '''Returns a list of categories'''
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories},
        }), 200

    @app.route('/questions', methods=['GET'])
    def get_questions():
        '''Returns a list of questions'''
        all_questions = Question.query.order_by(Question.id).all()

        questions = paginate_questions(request, all_questions)
        current_category = [question['category'] for question in questions]
        current_category = list(set(current_category))
        categories = Category.query.order_by(Category.type).all()

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(all_questions),
            'categories': {category.id: category.type for category in categories},
            'current_category': current_category,
        }), 200

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''Deletes a question by id'''
        try:
            question = Question.query.get(question_id)

            if not question:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
            }), 200

        except Exception as e:
            abort(404)

    @app.route('/questions', methods=['POST'])
    def add_question():
        '''Creates a new question'''
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if question is None or answer is None:
            abort(400)

        if len(question) == 0 or len(answer) == 0:
            abort(400)

        try:
            question = Question(question, answer, category, difficulty)

            question.insert()

            return jsonify({
                'success': True
            }), 201
        except Exception as e:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        '''Searchs questions'''
        search_term = request.json['searchTerm']

        if search_term is None:
            abort(400)

        if len(search_term) == 0:
            abort(400)

        try:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            search_results = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': search_results,
                'total_questions': len(search_results),
                'current_category': None
            }), 200
        except Exception:
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        '''Gets questions by category id'''
        selection = Question.query.filter_by(category=category_id).all()
        questions = paginate_questions(request, selection)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(selection),
            'current_category': category_id,
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        '''Allows users to play the quiz game'''
        previous_questions = request.json['previous_questions']
        category = request.json['quiz_category']

        try:
            if category['id'] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter_by(category=category['id']).filter(
                    Question.id.notin_(previous_questions)).all()

            if len(questions) == 0:
                raise

            question_list = [(query.id, query.question, query.answer)
                             for query in questions]

            question = questions[random.randrange(
                0, len(questions))].format() if len(questions) > 0 else None

            return jsonify({
                'success': True,
                'question': question
            })

        except Exception:
            abort(404)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app
