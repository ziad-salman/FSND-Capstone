import os
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, DateTime
from flask_migrate import Migrate
from datetime import datetime

database_name = "Capstone"

database_path = "postgres://{}:{}@{}/{}".format(
    'postgres', '4728', 'localhost:5432', database_name)
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


#Movie_class

class Movie(db.Model):
   
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False )
    release_date = Column(DateTime(), nullable=False)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    
    def update(self):
        db.session.commit()

    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }


#Actor_class

class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender  
        }