'''employee routes'''
from flask_jwt_extended import jwt_required
from models.models import Users, db
from sqlalchemy import func
from flask import (
    Blueprint,
    request,
    current_app,
    jsonify
)
from ..utils import(
    check_auth_status
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/get_employees', methods=['GET'])
@jwt_required()
def get_employees():
    '''fetch all employees'''
    if not check_auth_status('admin'):
        return jsonify({
            'error': 'Not authorized'
        }), 403
    offset = max(request.args.get('offset', 0, int), 0)
    limit = max(min(request.args.get('limit', 20, int), 100), 20)
    action = request.args.get('action')
    total = 0
    serialized_data = []
    try:
        #fetch employees to assign tasks
        if action == 'assign_task':
            employees = db.session.query(Users.user_id, Users.first_name, Users.last_name, Users.email).offset(offset).limit(limit).all()
        #normal fetching of employees
        else:
            employees = db.session.query(func.count().over().label('total'), Users).offset(offset).limit(limit).all()
        if not employees:
            return jsonify({
                'error': 'no employees found',
            }), 404
        if action == 'assign_task':
            serialized_data = [employee.to_dict() for employee in employees]
        else:
            total = employees[0].total
            serialized_data = [employee[1].to_dict() for employee in employees]
    except:
        current_app.logger.warning('Error fetching employees', exc_info=True)
    return jsonify({
        'employees': serialized_data,
        'count': {
            'page_count': len(serialized_data),
            'total': total
        }
    }), 200