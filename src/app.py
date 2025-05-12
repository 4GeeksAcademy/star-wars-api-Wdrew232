"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Vehicle, Favorites
from models import fetch_swapi_data  # Import SWAPI fetch function

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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

# -------------------- Fetch --------------------


@app.route('/fetch-swapi', methods=['GET'])
def fetch_swapi():
    """Fetch data from SWAPI.dev and store it in the database."""
    fetch_swapi_data()
    return jsonify({"message": "SWAPI data fetched successfully!"}), 200

# -------------------- USERS --------------------


@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    if "email" not in data:
        return jsonify({"error": "Missing email"}), 400

    new_user = User(email=data["email"])
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
    if "name" not in data:
        return jsonify({"error": "Missing name"}), 400

    new_character = Character(
        name=data["name"],
        species=data.get("species", "Unknown"),
        homeworld=data.get("homeworld", "Unknown"),
        affiliation=data.get("affiliation", "Unknown")
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
    if "name" not in data:
        return jsonify({"error": "Missing name"}), 400

    new_planet = Planet(
        name=data["name"],
        climate=data.get("climate", "Unknown"),
        terrain=data.get("terrain", "Unknown"),
        population=data.get("population", None)
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

# -------------------- VEHICLES --------------------


@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([vehicle.serialize() for vehicle in vehicles]), 200


@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    return jsonify(vehicle.serialize()), 200


@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Missing name"}), 400

    new_vehicle = Vehicle(
        name=data["name"],
        model=data.get("model", "Unknown"),
        manufacturer=data.get("manufacturer", "Unknown"),
        cost_in_credits=data.get("cost_in_credits", "Unknown"),
        length=data.get("length", None),
        max_atmosphering_speed=data.get("max_atmosphering_speed", "Unknown"),
        crew=data.get("crew", "Unknown"),
        passengers=data.get("passengers", "Unknown")
    )
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify(new_vehicle.serialize()), 201


@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted"}), 200

# -------------------- FAVORITES --------------------


@app.route('/favorites', methods=['GET'])
def get_favorites():
    favorites = Favorites.query.all()
    return jsonify([fav.serialize() for fav in favorites]), 200


@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['POST'])
def add_favorite_vehicle(vehicle_id):
    data = request.json
    user = User.query.get(data["user_id"])
    vehicle = Vehicle.query.get(vehicle_id)

    if not user or not vehicle:
        return jsonify({"error": "Invalid user or vehicle"}), 404

    new_fav = Favorites(user_id=user.id, vehicle_id=vehicle.id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201


@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_favorite_vehicle(vehicle_id):
    data = request.json
    fav = Favorites.query.filter_by(
        user_id=data["user_id"], vehicle_id=vehicle_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite vehicle removed"}), 200


# Run the API
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
