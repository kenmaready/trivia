import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(page, selection):
  """helper function to return a selected number of results for pagination purposes"""
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  return [question.format() for question in selection[start:end]]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    
    try:
      categories = {category.id : category.type for category in Category.query.all()}
      return jsonify({
        'success': True,
        'categories': categories
      })

    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    page = request.args.get('page', 1, type=int)

    try:
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(page, selection)
      if len(current_questions) == 0:
        abort(404)


      total_questions = len(selection)

      categories = {category.id : category.type for category in Category.query.all()}

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": total_questions,
        "categories": categories,
        "current_category": None
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
    except:
      abort(404)

    if question:    
      try:
        question.delete()
      except:
        abort(500)
      finally:
        return jsonify({ "success": True })
    
    else:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def search_or_add_question():
    body = request.get_json()

    search_term = body.get('searchTerm', None)
    if search_term:
      try:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
        page = request.args.get('page', 1, type=int)
        questions = paginate_questions(page, selection)
        total_questions = len(selection)

      except:
        abort(500)
      
      finally:
        return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': total_questions,
          'current_category': None
        })

    else:
      question = body.get('question', None)
      answer = body.get('answer', None)    
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)

      if question and answer and difficulty and category:
        try:
          new_question = Question(
            question = question,
            answer = answer,
            difficulty = difficulty,
            category = category
          )
          new_question.insert()

        except:
          abort(500)

        finally:
          return jsonify({ "success": True })
      
      else:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 

  NOTE: See above (added into add_book functionality because both used same endpoint & method)
  '''
  

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    
    # check to be sure category_id supplied actually exists as valid category
    category_check = Category.query.get(category_id)
    if not category_check:
      abort(404)

    page = request.args.get('page', 1, type=int)

    try:
      selection = Question.query.order_by(Question.id).filter(Question.category == str(category_id)).all()
      current_questions = paginate_questions(page, selection)
      total_questions = len(selection)

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": total_questions,
        "current_category": category_id
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()

    previous_questions = body['previous_questions']
    category_id = int(body['quiz_category']['id'])

    try:
      if category_id == 0:
        questions = Question.query.order_by(Question.id).filter(~Question.id.in_(previous_questions)).all()
      elif category_id >= 1 and category_id <= 6:
        questions = Question.query.order_by(Question.id).filter(Question.category == str(category_id)).filter(~Question.id.in_(previous_questions)).all()
      else:
        error_code = 404
        abort(error_code)

      if questions:
        question = random.choice(questions).format()

        return jsonify({
          'success': True,
          'question': question
        })
      
      else:
        return jsonify({
          'success': True
        })

    except:
      abort(error_code or 500)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "You may need to come to terms with the very real possibility that the resource you are seeking does not exist."
      }), 404
  
  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Naughty user. There you go again, trying a method that is not allowed. Tsk tsk."
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "I'm good, but even I cannot process this request. Something needs to be changed."
      }), 422
  
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "I need to tell you something ... I screwed up. Something has gone wrong in my servers or my database. Your action has not been completed."
      }), 500


  return app

    