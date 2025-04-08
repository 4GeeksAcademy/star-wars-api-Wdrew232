"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for # type: ignore
from flask_migrate import Migrate # type: ignore
from flask_cors import CORS # type: ignore
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Character,Planet,fav_character
#from models import Person

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

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_get_user():
    user = User.query.all()
    user_list = [userData.serialize() for userData in user]

    return jsonify(user_list), 200

@app.route('/character', methods=['GET'])
def handle_get_Character():
    character = Character.query.all()
    character_list = [characterData.serialize() for characterData in character]

    return jsonify(character_list), 200


@app.route('/planets', methods=['GET'])
def handle_get_planet():
    planets = Planet.query.all()
    planets_list = [planetData.serialize() for planetData in planets]

    return jsonify(planets_list), 200

@app.route('/fav_character', methods=['GET'])
def handle_get_fav():
    fav = fav_character.query.all()
    favorite_list = [fav_character.serialize() for favData in fav ]

    return jsonify(favorite_list), 200


@app.route('/user', methods=['POST'])
def handle_user_post():
    data = request.json
    new_user = User(
        id = data["id"], 
        email = data["email"], 
        password = data["password"], 
        is_active = data["is_active"] 
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 200

@app.route('/character', methods=['POST'])
def handle_character_post():
    data = request.json
    new_character = Character(
        id = data["id"],
        name = data["name"],
        age = data["age"],
        height =  data["height"],
        weight = data["weight"]
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 200

@app.route('/planets', methods=['POST'])
def handle_planet_post():
    data = request.json
    new_planet = Planet(
        id = data["id"],
        name = data["name"],
        population = data["population"],
        size = data["size"]
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 200

@app.route('/fav_character', methods=['POST'])
def handle_fav_post():
    data = request.json
    new_fav = User(
       user_id = data["user_id"], 
       character_id = data["character_id"]
    )
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
