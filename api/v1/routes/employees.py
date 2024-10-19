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
from ..utils import gen_uuid

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/get_tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    '''fetch all tasks'''
    offset = max(request.args.get('offset', 0, int), 0)
    limit = max(min(request.args.get('limit', 20, int), 100), 20)
    identity = get_jwt_identity()
    email = identity['email']
    try:
        tasks = db.session.query(Tasks).offset(offset).limit(limit).filter_by(email=email).all()
        if not tasks:
            return jsonify({
                'error': 'no tasks found',
            }), 404
        serialized_data = [task.to_dict() for task in tasks]
    except:
        current_app.logger.warning('Error fetching tasks', exc_info=True)
    return jsonify({
        'tasks': serialized_data
    }), 200

@employees_bp.route('/add_tasks', methods=['POST'])
@jwt_required()
def add_tasks():
    '''add a new task'''
    #validate schema
    payload = request.get_json()
    schema = task_schema()
    validation_err = schema.load(payload)
    if validation_err:
        return jsonify({
            'error': 'Invalid input'
        }), 400
    identity = get_jwt_identity()
    email = identity['email']
    new_task = Tasks(
        task_id = gen_uuid(),
        task_name = payload['taskName'],
        description = payload['description'],
        team = payload['team'],
        started = payload['started'],
        to_end = payload['toEnd'],
        priority = payload['priority'],
        status = 'pending',
        user_id = ''
    )

