from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
 
import src.models # Is needed for tables to be created!

def create_tables():
    db.drop_all()
    db.create_all()

