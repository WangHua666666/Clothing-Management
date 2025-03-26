from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Clothing(db.Model):
    __tablename__ = 'clothing'
    id = db.Column(db.String(50), primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    style = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(50), nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.now)
    cost_price = db.Column(db.Float, nullable=False)
    retail_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Clothing {self.id}>'
