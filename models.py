from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    wallet = db.Column(db.Float, default=0.0)

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    ambulance_number = db.Column(db.String(50), nullable=False)
    service_type = db.Column(db.String(50), nullable=False) # 'Human' or 'Animal'
    wallet = db.Column(db.Float, default=0.0)
    current_location = db.Column(db.String(255), default="Delhi, India")
    provider_lat = db.Column(db.Float, nullable=True)
    provider_lng = db.Column(db.Float, nullable=True)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    wallet = db.Column(db.Float, default=0.0)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    available = db.Column(db.Boolean, default=True)
    hospital = db.relationship('Hospital', backref=db.backref('doctors', lazy=True))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), unique=True, nullable=False)
    provider_name = db.Column(db.String(150), nullable=False)
    ambulance_number = db.Column(db.String(50), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    booked_by_name = db.Column(db.String(150), nullable=False)
    booked_by_mobile = db.Column(db.String(15), nullable=False)
    booked_by_username = db.Column(db.String(80), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    pickup_lat = db.Column(db.Float, nullable=True)
    pickup_lng = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default="Pending") # Pending, Accepted, Rejected, Completed
    assigned_doctor = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
