import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category
import json
import collections


QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # this endpoint gets all categories
    @app.route('/categories')
    def get_categories():
        # get all catgories in the database
        categories = Category.query.all()
        categories_list = {}

        categories_list = collections.defaultdict(list)
        for category in categories:
            categories_list[category.id].append(category.type)
        # no categories found
        if len(categories_list) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories_list
        })

    # this endpoint gets all questions
    @app.route('/questions')
    def get_questions():

        questions = Question.query.all()
        formatted_questions = paginate_questions(request, questions)

        categories = Category.query.all()
        categories_list = {}
        categories_list = collections.defaultdict(list)

        for category in categories:
            categories_list[category.id].append(category.type)

        # no questions found
        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': categories_list
        })

    # the next endpoint deletes question using id
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # get the question by its id to be deleted
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            questions = Question.query.order_by(Question.id).all()
            formatted_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': formatted_questions,
                'total_questions': len(questions),
            })

        except BaseException:
            abort(422)

        # this endpoint handels adding new questions
    @app.route('/questions', methods=['POST'])
    def post_question():

        Request_body = request.get_json()

        question = Request_body.get('question', None)
        answer = Request_body.get('answer', None)
        difficulty = Request_body.get('difficulty', None)
        category = Request_body.get('category', None)

        if ((question is None) or (answer is None) or (
                difficulty is None) or (category is None)):
            abort(422)

        try:
            # create new question object
            questionObject = Question(question=question, answer=answer,
                                      difficulty=difficulty, category=category)
            questionObject.insert()

            questions = Question.query.order_by(Question.id).all()
            formatted_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'created': questionObject.id,
                'questions': formatted_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            abort(422)

    # the next endpoint handels serching of questions

    @app.route('/search', methods=['POST'])
    def search():

        # if the search term is there, the if body will be executed
        if (request.get_json().get('searchTerm') != ""):
            search_phrase = request.get_json().get('searchTerm')
            result = Question.query.filter(
                Question.question.ilike('%' + search_phrase + '%')).all()

            # 404 if no results found
            if len(result) == 0:
                abort(404)

            formatted_questions = paginate_questions(request, result)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(Question.query.all())
            })

    # this endpoint will get questions based on specific category
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):

        try:
            category = Category.query.filter(Category.id == id).one_or_none()
            result = Question.query.filter(
                Question.category == category.id).all()
            formatted_questions = paginate_questions(request, result)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(Question.query.all()),
                'current_category': category.type
            })

        except BaseException:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():

        Request_body = request.get_json()

        previous = Request_body.get('previous_questions')
        category = Request_body.get('quiz_category')

        # if all category is selected
        if (category['id'] == 0):
            questions = Question.query.all()

        else:
            questions = Question.query.filter(
                Question.category == category['id']).all()

        total = len(questions)
        random_num = random.randrange(0, total, 1)
        question = questions[random_num]

        # the loop will continue until it finds unuded question
        i = 0
        while (len(previous) > i):
            flag = True
            random_num = random.randrange(0, total, 1)
            question = questions[random_num]

            for pre in previous:
                if (pre == question.id):
                    flag = False

            if flag:
                i += 1
            # if all questions are tried,return without question
            if (len(previous) == total):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

# error handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
