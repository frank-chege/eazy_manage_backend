from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from .base_model import Base_model

db = SQLAlchemy()

class Users(db.Model, Base_model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), unique=True, primary_key=True)
    role = db.Column(db.Enum('admin', 'user'), default='user', nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contact = db.Column(db.String(30), unique=True, nullable=False)
    emergency_contact = db.Column(db.String(30), unique=True, nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'trans', 'other'), nullable=False)
    status = db.Column(db.Enum('active', 'leave', 'inactive'), default='active')
    department = db.Column(db.Enum('ACCOUNTS', 'IT', 'HR', 'KITCHEN'), nullable=False)
    job_title = db.Column(db.Enum('software_eng', 'hr', 'manager', 'chef', 'accoutant'), nullable=False)
    national_id = db.Column(db.Integer, unique=True, nullable=True)
    joined = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    
    # relationships
    task = relationship('Tasks', back_populates='user_id')

class Tasks(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.String(36), unique=True, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    team = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    started = db.Column(db.DateTime)
    planned_end_date = db.Column(db.Date)
    ended = db.Column(db.DateTime)
    priority = db.Column(db.Enum('high', 'medium', 'low'), default='high')
    status = db.Column(db.Enum('pending', 'complete'), default='pending')
    notes = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    #fk
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
