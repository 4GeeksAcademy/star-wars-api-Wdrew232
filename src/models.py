import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

db = SQLAlchemy()

# User Model


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)

    # Relationships
    favorites = relationship("Favorites", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }

# Character Model


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=True)
    homeworld: Mapped[str] = mapped_column(String(50), nullable=True)
    affiliation: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships
    favorites = relationship("Favorites", back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "homeworld": self.homeworld,
            "affiliation": self.affiliation
        }

# Planet Model


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(50), nullable=True)
    terrain: Mapped[str] = mapped_column(String(50), nullable=True)
    population: Mapped[int] = mapped_column(nullable=True)

    # Relationships
    favorites = relationship("Favorites", back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

# Vehicle Model


class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(50), nullable=True)
    cost_in_credits: Mapped[str] = mapped_column(String(50), nullable=True)
    length: Mapped[float] = mapped_column(nullable=True)
    max_atmosphering_speed: Mapped[str] = mapped_column(
        String(50), nullable=True)
    crew: Mapped[str] = mapped_column(String(50), nullable=True)
    passengers: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships
    favorites = relationship("Favorites", back_populates="vehicle")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "cost_in_credits": self.cost_in_credits,
            "length": self.length,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "crew": self.crew,
            "passengers": self.passengers
        }

# Favorites Model


class Favorites(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planet.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="favorites")
    character = relationship("Character", back_populates="favorites")
    planet = relationship("Planet", back_populates="favorites")
    vehicle = relationship("Vehicle", back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
            "vehicle_id": self.vehicle_id
        }

# Function to Fetch Data from SWAPI


def fetch_swapi_data():
    """Fetch characters, planets, and vehicles from SWAPI.dev and store them in the database."""

    # Fetch Characters
    character_url = "https://swapi.dev/api/people/"
    response = requests.get(character_url)
    if response.status_code == 200:
        characters = response.json()["results"]
        for char in characters:
            # Fetch species name if available
            species_name = "Unknown"
            if char.get("species") and len(char["species"]) > 0:
                species_response = requests.get(char["species"][0])
                if species_response.status_code == 200:
                    species_name = species_response.json().get("name", "Unknown")

            # Fetch homeworld name if available
            homeworld_name = "Unknown"
            if char.get("homeworld"):
                homeworld_response = requests.get(char["homeworld"])
                if homeworld_response.status_code == 200:
                    homeworld_name = homeworld_response.json().get("name", "Unknown")

            new_character = Character(
                name=char["name"],
                species=species_name,
                homeworld=homeworld_name,
                affiliation="Unknown"
            )
            db.session.add(new_character)

    # Fetch Planets
    planet_url = "https://swapi.dev/api/planets/"
    response = requests.get(planet_url)
    if response.status_code == 200:
        planets = response.json()["results"]
        for planet in planets:
            # Handle population parsing
            population_value = planet["population"]
            if population_value.isdigit():
                population_value = int(population_value)
            else:
                population_value = None  # Set to None if "unknown" or "N/A"

            new_planet = Planet(
                name=planet["name"],
                climate=planet["climate"],
                terrain=planet["terrain"],
                population=population_value
            )
            db.session.add(new_planet)

    # Fetch Vehicles
    vehicle_url = "https://swapi.dev/api/vehicles/"
    response = requests.get(vehicle_url)
    if response.status_code == 200:
        vehicles = response.json()["results"]
        for vehicle in vehicles:
            new_vehicle = Vehicle(
                name=vehicle["name"],
                model=vehicle["model"],
                manufacturer=vehicle["manufacturer"],
                cost_in_credits=vehicle["cost_in_credits"],
                length=float(vehicle["length"]) if vehicle["length"].replace(
                    '.', '', 1).isdigit() else None,
                max_atmosphering_speed=vehicle["max_atmosphering_speed"],
                crew=vehicle["crew"],
                passengers=vehicle["passengers"]
            )
            db.session.add(new_vehicle)

    db.session.commit()
