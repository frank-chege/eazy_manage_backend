from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), unique=True, primary_key=True)
    role = db.Column(db.Enum('admin', 'user'), default='user')
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contact = db.Column(db.String(30), unique=True, nullable=False)
    emergency_contact = db.Column(db.String(30), unique=True, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'trans', 'other'))
    status = db.Column(db.Enum('active', 'on_leave', 'inactive'))
    address = db.Column(db.String(255), nullable=False)
    marital_status = db.Column(db.Enum('single', 'married'))
    department = db.Column(db.String(50), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.Integer, unique=True)
    kra_pin = db.Column(db.String(50), nullable=False)
    joined = db.Column(db.Date, nullable=False)
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
