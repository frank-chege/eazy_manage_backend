'''employee routes'''
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import Users, db, Organizations
from sqlalchemy import func
from flask import (
    Blueprint,
    request,
    current_app,
    jsonify
)
from ..utils import(
    check_auth_status,
    gen_uuid,
    create_random_num,
    send_email
)
from ..schema import auth_schema
from marshmallow import ValidationError

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/reg_employee', methods=['POST'])
@jwt_required()
def reg_employee():
    '''user registration endpoint'''
    payload = request.get_json()
    #validate payload
    schema = auth_schema('register')
    try:
        new_user = schema.load(payload)
    except ValidationError as err:
        current_app.logger.error(f'Schema error on employee registration, {err}')
        return jsonify({
            'error': err
        }), 400
    email = payload['email']
    first_name = payload['first_name']
    last_name = payload['last_name']
    identity = get_jwt_identity()
    org_id = identity['org_id']
    #check if user exists
    user = db.session.query(Users).filter_by(email=email).first()
    if user:
        return jsonify({
            'error': 'Employee already exists'
        }), 409
    #add new user
    new_user['user_id'] = gen_uuid()
    new_user['org_id'] = org_id
    new_user = Users(**new_user)
    password = create_random_num()
    new_user.set_pwd(password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error(f'Registration failed', exc_info=True)
        return jsonify({
            'error': 'An error occured. Please try again'
        }), 500
    org_name = db.session.query(Organizations.name).filter(Organizations.org_id == org_id).first()
    if org_name != 'loading':
        #send email
        body = f'You have been registered as an employee at {org_name}\
            Your one time password is {password}. Use to access your account and set your preffered one.'
        subject = 'Eazy manage registration'
        recipients = [email]
        send_email(subject, recipients, body)
    return jsonify(
        {
            'message': f'Successfully added employee {first_name} {last_name}'
        }
    ), 201

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
    identity = get_jwt_identity()
    org_id = identity['org_id']
    try:
        #get employees to assign tasks
        if action == 'assign_task':
            query = db.session.query(Users.user_id, Users.first_name, Users.last_name, Users.email)
        #getting employees in the org
        else:
            query = db.session.query(func.count().over().label('total'), Users)
        #filter by org
        employees = query.filter(Users.org_id == org_id).offset(offset).limit(limit).all()
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