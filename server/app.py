#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Review, Game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return "Game Review API"

@app.route('/games')
def games():
    games = [game.to_dict() for game in Game.query.all()]
    return make_response(games, 200)

@app.route('/games/<int:id>')
def game_by_id(id):
    game = Game.query.get(id)
    if game:
        return make_response(game.to_dict(), 200)
    return make_response({"error": "Game not found"}, 404)

@app.route('/users')
def users():
    users = [user.to_dict() for user in User.query.all()]
    return make_response(users, 200)

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'GET':
        reviews = [review.to_dict() for review in Review.query.all()]
        return make_response(reviews, 200)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['score', 'comment', 'game_id', 'user_id']
        if not all(field in data for field in required_fields):
            return make_response({"error": "Missing required fields"}, 400)
        
        try:
            new_review = Review(
                score=data['score'],
                comment=data['comment'],
                game_id=data['game_id'],
                user_id=data['user_id']
            )
            db.session.add(new_review)
            db.session.commit()
            return make_response(new_review.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

@app.route('/reviews/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def review_by_id(id):
    review = Review.query.get(id)
    
    if not review:
        return make_response({"error": "Review not found"}, 404)
    
    if request.method == 'GET':
        return make_response(review.to_dict(), 200)
    
    elif request.method == 'PATCH':
        data = request.get_json()
        
        try:
            for attr in data:
                if attr in ['score', 'comment']:  # Only allow updating these fields
                    setattr(review, attr, data[attr])
            db.session.commit()
            return make_response(review.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(review)
            db.session.commit()
            return make_response({"message": "Review deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)