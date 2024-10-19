'''employee routes'''
from flask_jwt_extended import jwt_required
from models.models import Users, db
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
    try:
        employees = db.session.query(Users).offset(offset).limit(limit).all()
        if not employees:
            return jsonify({
                'error': 'no employees found',
            }), 404
        serialized_data = [employee.to_dict() for employee in employees]
    except:
        current_app.logger.warning('Error fetching employees', exc_info=True)
    return jsonify({
        'employees': serialized_data
    }), 200