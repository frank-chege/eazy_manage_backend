'''employee routes'''
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import Users, db, Tasks
from flask import (
    Blueprint,
    request,
    current_app,
    jsonify
)
from ..utils import gen_uuid, check_task_schema, send_email
from sqlalchemy import func, and_
import json
from datetime import datetime, timedelta

tasks_bp = Blueprint('tasks', __name__)

#get tasks
@tasks_bp.route('/get_tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    '''fetch all tasks'''
    pagination = json.loads(request.args.get('pagination'))
    if pagination:
        offset = max(int(pagination.get('offset', 0)), 0)
        limit = max(min(int(pagination.get('limit', 20)), 100), 20)
    else:
        offset = 0
        limit = 20
    status = request.args.get('status', 'pending')
    filter = json.loads(request.args.get('filter'))
    from_date = None
    to_date = None
    if filter:
        from_date = filter.get('from') 
        to_date = filter.get('to')
        filter_user_id = filter.get('employeeId')
    identity = get_jwt_identity()
    role = identity['role']
    serialized_data = []
    total = 0
    try:
        #admin request
        if role == 'admin':
            query = db.session.query(func.count().over().label('total'),Tasks, Users)\
            .join(Users, Tasks.user_id == Users.user_id)\
            .filter(Tasks.status == status)
            #filter by employee
            if filter_user_id:
                query = query.filter(Tasks.user_id == filter_user_id)
        #employee request
        else:
            user_id = identity['user_id']
            query = db.session.query(func.count().over().label('total'),Tasks)\
            .filter(Tasks.user_id == user_id, Tasks.status == status)
        #filter by date
        if to_date and from_date:
            formated_to_date = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter((and_(Tasks.started >= from_date, Tasks.started < (formated_to_date + timedelta(days=1))))\
                    if status == 'pending' else\
                    query.filter(and_(Tasks.ended >= from_date, Tasks.ended < (formated_to_date + timedelta(days=1)))))
        query = query.order_by(Tasks.started.desc()) if status == 'pending' else query.order_by(Tasks.ended.desc())
        tasks = query.offset(offset).limit(limit).all()
        if not tasks:
            return jsonify({
                'error': 'no tasks found',
            }), 404
        total = tasks[0].total
        user_data = lambda user : {
            'first_name': user['first_name'],
            'last_name': user['last_name']
        }
        serialized_data = [
            {
             **task[1].to_dict(),
            'user': user_data(task[2].to_dict())
        } if role == 'admin' else task[1].to_dict()
            for task in tasks
        ]
    except:
        current_app.logger.warning('Error fetching tasks', exc_info=True)
    return jsonify({
        'tasks': serialized_data,
        'count': {
            'page_count': len(serialized_data),
            'total': total
        }
    }), 200

#add a new task
@tasks_bp.route('/new_task', methods=['POST'])
@jwt_required()
def new_task():
    '''add a new task'''
    #validate admin
    identity = get_jwt_identity()
    role = identity['role']
    #validate schema
    payload = request.get_json()
    if role == 'admin':
        validation_err = check_task_schema(payload, 'add_new_task', role)
    else:
        validation_err = check_task_schema(payload, 'add_new_task', role='employee')
    if validation_err is not True:
        return jsonify({
            'error': validation_err
        }), 400
    task_name = payload['taskName']
    description = payload['description']
    employee_id =  payload['employeeId'] if role == 'admin' else None
    new_task = Tasks(
        task_id = gen_uuid(),
        task_name = task_name,
        description = description,
        #team = payload['team'],
        started = payload['started'],
        to_end = payload['toEnd'],
        priority = payload['priority'],
        status = 'pending',
        user_id = employee_id if role == 'admin' else identity['user_id']
    )
    try:
        db.session.add(new_task)
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error('An error occured while adding a new task', exc_info=True)
        return jsonify({
            'error': 'An error occured please try again'
        }), 500
    #notify employee of task issued
    if role == 'admin':
        try:
            email = db.session.query(Users.email).filter(Users.user_id == employee_id).first()[0]
        except:
            current_app.logger.error('Error fetching email', exc_info=True)
        if email:
            body = f'You have been assigned a new task.\n\
                Task name: {task_name}\n\
                    Task description: {description}\n\
                        Log in to your account to view the task'
            subject = 'New task available'
            recipients = [email]
            send_email(subject, recipients, body)
    return jsonify({
        'message': 'New task added successfully'
    }), 201

#update task status
@tasks_bp.route('/change_status', methods=['PUT'])
@jwt_required()
def change_task_status():
    '''change the status of a task'''
    payload = request.get_json()
    #validate schema
    validation_err = check_task_schema(payload, 'change_status', role='')
    if validation_err is not True:
        return jsonify({
            'error': validation_err
        }), 400
    task_id = payload['taskId']
    new_status = payload['newStatus']
    #verify task exists
    task = db.session.query(Tasks).filter_by(task_id=task_id).first()
    if not task:
        return jsonify({
            'error': 'Task not found'
        }), 404
    #update task status
    try:
        task.status = new_status
        if new_status == 'completed':
            task.ended = datetime.now()
        else:
            task.ended = None
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error('Task status update failed', exc_info=True)
        return jsonify({
            'error': 'Task status update failed. Try again'
        }), 500
    return jsonify({
        'message': 'Task status changed'
    }), 200