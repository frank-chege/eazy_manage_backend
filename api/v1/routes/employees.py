'''employee routes'''
from flask_jwt_extended import jwt_required
from models.models import Users, db

from flask import (
    Blueprint,
    request
)

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/view_all', methods=['GET'])
@jwt_required()
def view_all():
    '''fetch all employees'''
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    
