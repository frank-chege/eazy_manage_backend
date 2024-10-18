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

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/get', methods=['GET'])
@jwt_required()
def get():
    '''fetch all employees'''
    if not check_auth_status('admin'):
        return jsonify({
            'error': 'Not authorized'
        }), 403
    offset = max(request.args.get('offset', 0, int), 0)
    limit = max(min(request.args.get('limit', 20, int), 100), 20)
    try:
        data = db.session.query(Users).offset(offset).limit(limit).all()
        if not data:
            return jsonify({
                'error': 'no employees found',
            }), 404
    except:
        current_app.logger.warning('Error fetching employees', exc_info=True)
    return jsonify({
        'employees': data
    }), 200