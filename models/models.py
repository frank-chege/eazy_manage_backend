from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from .base_model import Base_model

db = SQLAlchemy()

class Users(db.Model, Base_model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), unique=True, primary_key=True)
    role = db.Column(db.Enum('admin', 'employee'), default='employee', nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    #contact = db.Column(db.String(30), unique=True, nullable=False)
    #gender = db.Column(db.Enum('male', 'female', 'trans', 'other'), nullable=False)
    status = db.Column(db.Enum('active', 'leave', 'inactive'), default='active')
    department = db.Column(db.Enum('ACCOUNTS', 'IT', 'HR'), nullable=False)
    job_title = db.Column(db.Enum('hr', 'developer', 'accoutant'), nullable=False)
    #national_id = db.Column(db.Integer, unique=True, nullable=True)
    joined = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    
    # relationships
    task = relationship('Tasks', back_populates='user')

    def to_dict(self):
        '''convert model to dictionary'''
        return {
            'user_id': self.user_id,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'status': self.status,
            'department': self.department,
            'job_title': self.job_title,
            'joined': self.joined.strftime('%Y-%m-%d') if self.joined else None
        }


class Tasks(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.String(36), unique=True, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    team = db.Column(db.String(255), nullable=False)
    started = db.Column(db.DateTime)
    to_end = db.Column(db.Date)
    ended = db.Column(db.DateTime)
    priority = db.Column(db.Enum('high', 'medium', 'low'), default='high')
    status = db.Column(db.Enum('pending', 'complete'), default='pending')
    notes = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    #fk
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    #relationship
    user = relationship('Users', back_populates='task')

    def to_dict(self)->dict:
        '''return dict rep of the model'''
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'team': self.team,
            'description': self.description,
            'started': self.started.strftime('%Y-%m-%d %H:%M:%S') if self.started else None,  # Format datetime
            'planned_end_date': self.planned_end_date.strftime('%Y-%m-%d') if self.planned_end_date else None,  # Format date
            'ended': self.ended.strftime('%Y-%m-%d %H:%M:%S') if self.ended else None,  # Format datetime
            'priority': self.priority,
            'status': self.status,
            'notes': self.notes,
            'comments': self.comments,
        }