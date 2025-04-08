from flask_sqlalchemy import SQLAlchemy  # type: ignore
from sqlalchemy import String, Boolean, Integer, Float  # type: ignore
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    age: Mapped[str] = mapped_column(String(5),nullable=True)
    height: Mapped[float] = mapped_column(nullable=True)
    weight: Mapped[float] = mapped_column(nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "height": self.height,
            "weight": self.weight
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)
    size: Mapped[float] = mapped_column(nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "size": self.size
        }

class fav_character(db.Model):
    user_id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    characters: Mapped[list["Character"]] = relationship("Character", back_populates="user")
    user: Mapped["User"] = relationship("User", back_populates="characters")
    
    def serialize(self):
        return {
            "user_id": self.id,
            "character_id": self.email
        }