import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "trivia"

#database_path = "postgres://{}/{}".format('localhost:5432', database_name)

#postgres://localhost:5432/database_name
#database_path = 'postgresql://{}:{}@{}/{}'.format('postgres', 'root','localhost:5432', 'trivia')


#database_path = "postgres://   postgres/reem".format('localhost:5432', database_name)

#'postgresql://postgres:root@localhost:5432/todo'
#'postgresql://postgres:root@localhost:5432/todo'
database_path = 'postgresql://postgres:root@localhost:5432/trivia'
#database_path=postgresql://user:pass@localhost:5432/my_db

               
db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    
    db.app = app
    db.init_app(app)
    db.create_all()
    
    

'''
Question

'''
class Question(db.Model):  
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  category = Column(String)
  difficulty = Column(Integer)

  def __init__(self, question, answer, category, difficulty):
    self.question = question
    self.answer = answer
    self.category = category
    self.difficulty = difficulty

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
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty
    }

'''
Category

'''
class Category(db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)

  def __init__(self, type):
    self.type = type

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }