'''handles user authentication'''
from flask_jwt_extended import (create_access_token,
                                jwt_required, get_jwt_identity,
                                create_refresh_token,
                                set_access_cookies,
                                set_refresh_cookies,
                                unset_jwt_cookies,
                                get_csrf_token)
from flask import request, jsonify, Blueprint, current_app, make_response, redirect, url_for, session
from ..schema import auth_schema, org_schema
from marshmallow import ValidationError
from ..utils import (
    send_email,
    create_random_num,
    hash_pwd,
    check_pwd,
    redis_client,
    gen_uuid
)
from models.models import db, Tasks, Users, Organizations
from datetime import datetime
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/org', methods=['POST'])
def register_org():
    '''registers an organization'''
    payload = request.get_json()
    #validate payload
    schema = org_schema()
    try:
        new_org_data = schema.load(payload)
    except ValidationError as err:
        current_app.logger.error(f'Schema error on register router, {err}')
        return jsonify({
            'error': err
        }), 400
    email = payload['email']
    org = db.session.query(Organizations).filter_by(email=email).first()
    if org:
        return jsonify({
            'error': 'Organization already exists'
        }), 409
    #create new org
    org_id = gen_uuid()
    new_org_data['org_id'] = org_id
    new_org_data['account_type'] = 'free' #initial account type
    new_org_data['joined'] = datetime.now()
    new_org = Organizations(**new_org_data)
    #create a super admin account in the users table
    super_admin = Users(
        user_id = gen_uuid(),
        org_id = org_id,
        email = email,
        role = 'admin',
        joined = datetime.now()
    )
    password = create_random_num()
    super_admin.set_pwd(password)
    try:
        db.session.add(new_org)
        db.session.add(super_admin)
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error(f'Organization registration failed', exc_info=True)
        return jsonify({
            'error': 'An error occured. Please try again'
        }), 500
    #send email
    body = f'Thank you for registering with us. To continue, login with your email and this one time password\n\
        {password}.'
    subject = 'Eazymanager registration'
    recipients = [email]
    send_email(subject, recipients, body)
    return jsonify(
        {
            'message': f'Registration successful. Please check your email to continue.'
        }
    ), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    '''user login endpoint'''
    payload = request.get_json()
    #validate payload
    schema = auth_schema('login')
    try:
        schema.load(payload)
    except ValidationError as err:
        current_app.logger.error(f'Schema error on login, {err}')
        return jsonify({
            'error': 'Invalid email or password'
        }), 400
    #verify login credentials
    email = payload['email']
    password = payload['password']
    try:
        #check if user exists
        user = db.session.query(Users).filter_by(email=email).first()
        if not user:
            return jsonify({
                'error': 'Invalid email or password',
            }
            ), 404
        
        hashed_pwd = user.password
        role = user.role
        #verify password
        if not user.check_pwd(password, hashed_pwd):
            return jsonify({
                'error': 'Invalid email/password'
            }), 401
    except:
        current_app.logger.error(f'An error occured while logging in', exc_info=True)
        return jsonify({
            'error': 'An error occured! Please try again'
        }), 500
    #create access tokens
    identity = {
        'email': email,
        'role': role,
        'user_id': user.user_id,
        'org_id': user.org_id,
    }
    jwt_token = create_access_token(identity=identity)
    csrf_token = get_csrf_token(jwt_token)
    refresh_token = create_refresh_token(identity=identity)
    #create response
    response = make_response({
    'role': role,
    'token': csrf_token,
    'message': 'Login successful',
    })
    set_access_cookies(response, jwt_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200

@auth_bp.route('/check_auth_status', methods=['POST'])
@jwt_required()
def check_auth_status():
    '''checks the auth status'''
    payload = request.get_json()
    #validate payload
    schema = auth_schema('validate_role')
    try:
        schema.load(payload)
    except ValidationError as err:
        current_app.logger.error(f'Schema error on check_auth_status, {err}')
        return jsonify({
            'status': 'false',
            'message': 'Invalid request'
        }), 400
    identity = get_jwt_identity()
    role = payload['role']
    #verify admin
    if role == 'admin':
        if role != identity['role']:
            return jsonify({'status': 'false'}), 403
    return jsonify({'status': 'true'}), 200

@auth_bp.route('/start_password_reset', methods=['GET'])
@jwt_required()
def start_password_reset():
    '''start reset password process for logged in users'''
    identity = get_jwt_identity()
    email = identity['email']
    session['email'] = email
    return redirect(url_for('auth.get_reset_code')), 302

@auth_bp.route('/get_reset_code', methods=['POST', 'GET'])
def get_reset_code():
    '''get the password reset code'''
    #get email for logged in users
    if request.method == 'GET':
        email = session.get('email')
        if not email:
            return jsonify({
            'error': 'Email not found',
            'messsage': 'An error occured. Please try again.'
        }), 400
        session.pop('email')
    #get and verify email for non logged in users
    else:
        payload = request.get_json()
        #validate payload
        schema = auth_schema('get_reset_code')
        try:
            schema.load(payload)
        except ValidationError as err:
            current_app.logger.error(f'Schema error on get_reset_code, {err}')
            return jsonify({
                'error': err
            }), 400
        #check if user exists
        email = payload['email']
        try:
            user = db.session.query(Users).filter_by(email=email).first()
            if not user:
                return jsonify({
                'error': 'Invalid email! Please try again'
                }), 404
        except:
            current_app.logger.error('An error occured while querying user to reset password', exc_info=True)
            return jsonify({
                'error': 'An error occured! Please try again'
            }), 500
    #create reset code
    code = create_random_num()
    reset_token = gen_uuid()
    data = {
            'reset_code': code,
            'email': email
        }
    try:
        redis_client.setex(reset_token, 5*60, json.dumps(data))
    except:
        current_app.logger.error('An error occured while creating the reset code', exc_info=True)
        return jsonify({
            'error': 'An error occured! Please try again'
        }), 500
    subject = 'Eazy manage account password reset'
    body = f'You have requested to reset your password. Use the code below within 5 minutes to reset your passowrd\n\
            {code}\n\
            If you did not make this request please reach out to us immediately.'
    recipients = [email]
    send_email(subject, recipients, body)
    response = make_response({
        'message': 'Code sent successfully. Please check your email',
    })
    response.set_cookie('reset_token', reset_token, httponly=True)
    return response, 201

def get_user_data(request, redis_client)->dict:
    '''retrieve user data from memory'''
    reset_token = request.cookies.get('reset_token')
    if not reset_token:
        return {
            'status': False,
            'error': 'An error occured please request another code'
        }
    user_data = redis_client.get(reset_token)
    if not user_data:
        return {
            'status': False,
            'error': 'Session expired. Please request another code'
        }
    return {
        'status': True,
        'user_data': json.loads(user_data)
    }

@auth_bp.route('/verify_reset_code', methods=['POST'])
def verify_reset_code():
    '''verify code to reset password'''
    payload = request.get_json()
    #validate payload
    user_code = payload['reset_code']
    if not user_code or len(user_code) != 6 or not user_code.isdigit() :
        return jsonify({
            'error': 'Invalid code'
        }), 400
    #get user data
    resp = get_user_data(request, redis_client)
    if resp['status'] is False:
        return jsonify({
            'error': resp['error']
        }), 400
    user_data = resp['user_data']
    #verify code
    server_code = user_data['reset_code']
    if server_code != user_code:
        return jsonify({
            'error': 'Invalid code. Please try again or request a new code'
        }), 400
    return jsonify(
    {
        'message': 'Code successfully verified',
    }
    ), 200

@auth_bp.route('/create_new_password', methods=['POST'])
def create_new_password():
    '''create new password'''
    payload = request.get_json()
    #validate payload
    schema = auth_schema('create_new_password')
    try:
        schema.load(payload)
    except ValidationError as err:
        current_app.logger.error(f'Schema error on create new password, {err}')
        return jsonify({
            'error': err,
            'message': 'Invalid password format'
        }), 400
    password = payload['password']
    #get user data
    resp = get_user_data(request, redis_client)
    if resp['status'] is False:
        return jsonify({
            'error': resp['error']
        }), 400
    user_data = resp['user_data']
    email = user_data['email']
    try:
        user = db.session.query(Users).filter_by(email=email).first()
        user.set_pwd(password)
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error(f'Password reset failed', exc_info=True)
        return jsonify({
            'error': 'An error occured. Please try again'
        }), 500
    #send confirmation email
    subject = 'Eazy manage password reset successful'
    body = 'You have successfully reset your password. If this was not you please contact us immediately'
    recipients = [email]
    send_email(subject, recipients, body)
    return jsonify(
    {
        'message': 'Password reset successful',
    }
    ), 201
        
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    '''clears access tokens from cookies'''
    response =  make_response({
        'status': 'true'
        })
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/refresh_token', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    '''refresh auth tokens'''
    jwt_token = create_access_token(identity=get_jwt_identity())
    refresh_token = create_refresh_token(identity=get_jwt_identity())
    response = make_response({'message': 'true'})
    #implement secure cookies in production
    response.set_cookie('jwt_token', jwt_token)
    response.set_cookie('refresh_token', refresh_token)
    return response, 200