'''employee routes'''
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import Users, db, Tasks
from flask import (
    Blueprint,
    request,
    current_app,
    jsonify
)
from ..schema import auth_schema, task_schema
from ..utils import gen_uuid, check_task_schema

employees_bp = Blueprint('employees', __name__)

#get tasks
@employees_bp.route('/tasks/get_tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    '''fetch all tasks'''
    offset = max(request.args.get('offset', 0, int), 0)
    limit = max(min(request.args.get('limit', 20, int), 100), 20)
    status = request.args.get('status', 'pending')
    identity = get_jwt_identity()
    user_id = identity['user_id']
    try:
        tasks = db.session.query(Tasks)\
        .filter(Tasks.user_id == user_id, Tasks.status == status)\
        .offset(offset)\
        .limit(limit)\
            .all()
        if not tasks:
            return jsonify({
                'error': 'no tasks found',
            }), 404
        serialized_data = [task.to_dict() for task in tasks]
    except:
        current_app.logger.warning('Error fetching tasks', exc_info=True)
    return jsonify({
        'tasks': serialized_data,
        'total': len(serialized_data)
    }), 200

#add a new task
@employees_bp.route('/tasks/new_task', methods=['POST'])
@jwt_required()
def new_task():
    '''add a new task'''
    #validate schema
    payload = request.get_json()
    validation_err = check_task_schema(payload, 'add_new_task')
    if validation_err is not True:
        return jsonify({
            'error': validation_err
        }), 400
    identity = get_jwt_identity()
    new_task = Tasks(
        task_id = gen_uuid(),
        task_name = payload['taskName'],
        description = payload['description'],
        #team = payload['team'],
        started = payload['started'],
        to_end = payload['toEnd'],
        priority = payload['priority'],
        status = 'pending',
        user_id = identity['user_id']
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
    return jsonify({
        'message': 'New task added successfully'
    }), 201

#update task status
@employees_bp.route('/tasks/change_status', methods=['PUT'])
@jwt_required()
def change_task_status():
    '''change the status of a task'''
    payload = request.get_json()
    #validate schema
    validation_err = check_task_schema(payload, 'change_status')
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