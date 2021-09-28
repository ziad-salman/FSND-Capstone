import os
from flask import Flask, request, abort, jsonify, render_template, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor, db
from auth import AuthError, requires_auth
import datetime
from flask_migrate import Migrate




def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  migrate = Migrate(app, db)

  


  @app.after_request
  def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-type,Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Headers',
        'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    return response



  #--Movie-API

  @app.route('/movies')
  @requires_auth('get:movies')
  def get_movies(jwt):
  
    try:

      all_movies = Movie.query.all()

      if len(all_movies) == 0:
            abort(404)

      return jsonify({
        'success': True,
        'movies': [movie.format() for movie in all_movies]
      }), 200  
    except:
       abort(422)


  @app.route('/movies', methods=['POST'])
  @requires_auth('post:movie')
  def post_movie(payload):

    title = request.get_json().get('title')
    release_date = request.get_json().get('release_date')

    try:

        movie = Movie(title=title, release_date=release_date)
        movie.insert()

        return jsonify({
            'success': True,
            'movies': movie.format()
        }), 200      
    
    except:
       abort(422)


  @app.route('/movies/<id>', methods=['PATCH'])
  @requires_auth('patch:movie')
  def update_movie(payload, id):

    data = request.get_json()
    movie = Movie.query.get(id)
    if movie is None:
          abort(404)

    try:

        if 'title' in data:
             movie.title = data['title']

        if 'release_date' in data:
             movie.release_date = data['release_date']
        
        movie.update()
       
        
        return jsonify({
             'success': True,
             'movies': movie.format()
        }), 200
   
    except:
        abort(422)



  @app.route('/movies/<id>', methods=['DELETE'])
  @requires_auth('delete:movie')
  def delete_movie(payload, id):
    
    movie = Movie.query.get(id)
  
    if movie is None:
          abort(404)
   
    try:
      movie.delete()

      return jsonify({
        'success': True,
        'movies': id
      }), 200

    except:
        abort(422)

  #--Actor-API


  @app.route('/actors')
  @requires_auth('get:actors')
  def get_actors(payload):

    try:

      all_actors = Actor.query.all()

      if len(all_actors) == 0:
            abort(404)

      return jsonify({
        'success': True,
        'actors': [actor.format() for actor in all_actors]
      }), 200  
    except:
       abort(422)



  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actor')
  def post_actor(payload):

    name = request.get_json().get('name')
    age = request.get_json().get('age')
    gender = request.get_json().get('gender')

    try:

        actor = Actor(name=name, age=age, gender=gender)
        actor.insert()

        return jsonify({
            'success': True,
            'actors': actor.format()
        }), 200      
    
    except:
       abort(422)      



  @app.route('/actors/<id>', methods=['PATCH'])
  @requires_auth('patch:actor')
  def update_actor(payload, id):

    data = request.get_json()
    actor = Actor.query.get(id)
    if actor is None:
          abort(404)

    try:

        if 'name' in data:
             actor.name = data['name']

        if 'age' in data:
             actor.age = data['age']

        if 'gender' in data:
             actor.gender = data['gender']     
        
        actor.update()
        
        return jsonify({
             'success': True,
             'actors': actor.format()
        }), 200
   
    except:
        abort(422)



  @app.route('/actors/<id>', methods=['DELETE'])
  @requires_auth('delete:actor')
  def delete_actor(payload, id):
    
    actor = Actor.query.get(id)
  
    if actor is None:
          abort(404)
    try:
      actor.delete()

      return jsonify({
        'success': True,
        'actors': id
      }), 200

    except:
        abort(422)

  #--Error-handling

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": " Not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422

  app.errorhandler(409)
  def duplicate(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "Duplicate"
    }), 409

  @app.errorhandler(AuthError)
  def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code

  return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)