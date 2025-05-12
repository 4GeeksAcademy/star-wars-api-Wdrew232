"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorites

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# -------------------- USERS --------------------
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        email=data["email"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# -------------------- CHARACTERS --------------------
@app.route('/character', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([char.serialize() for char in characters]), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@app.route('/character', methods=['POST'])
def create_character():
    data = request.json
    new_character = Character(
        name=data["name"],
        age=data["age"],
        height=data["height"],
        weight=data["weight"]
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201

@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({"message": "Character deleted"}), 200

# -------------------- PLANETS --------------------
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.json
    new_planet = Planet(
        name=data["name"],
        population=data["population"],
        size=data["size"]
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted"}), 200

# -------------------- FAVORITES --------------------
@app.route('/favorites', methods=['GET'])
def get_favorites():
    favorites = Favorites.query.all()
    return jsonify([fav.serialize() for fav in favorites]), 200

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    data = request.json
    new_fav = Favorites(
        user_id=data["user_id"],
        character_id=character_id
    )
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.json
    new_fav = Favorites(
        user_id=data["user_id"],
        planet_id=planet_id
    )
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    fav = Favorites.query.filter_by(character_id=character_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite character removed"}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    fav = Favorites.query.filter_by(planet_id=planet_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite planet removed"}), 200

# Run the API
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
