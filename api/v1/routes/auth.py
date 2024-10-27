'''handles user authentication'''
from flask_jwt_extended import (create_access_token,
                                jwt_required, get_jwt_identity,
                                create_refresh_token,
                                set_access_cookies,
                                set_refresh_cookies,
                                unset_jwt_cookies,
                                get_csrf_token)
from flask import request, jsonify, Blueprint, current_app, make_response
from ..schema import auth_schema
from marshmallow import ValidationError
from ..utils import (
    send_email,
    create_random_num,
    hash_pwd,
    check_pwd,
    redis_client,
    gen_uuid
)
from models.models import db, Tasks, Users

auth_bp = Blueprint('auth', __name__)

def _check_schema(payload: dict, activity: str)->dict:
    '''validates the schema'''
    schema = auth_schema(activity)
    try:
        schema.load(payload)
        return True
    except ValidationError as err:
        return {
                'error':{
                    'type': 'ValidationError',
                    'message': err.messages
                }
            }

@auth_bp.route('/register', methods=['POST'])
def register():
    '''user registration endpoint'''
    payload = request.get_json()
    #validate payload
    validation_err = _check_schema(payload, 'register')
    if validation_err is not True:
        current_app.logger.error(f'Schema error on register router, {validation_err}')
        return jsonify({
            'error': validation_err
        }), 400
    email = payload['email']
    first_name = payload['firstName']
    last_name = payload['lastName']
    #check if user exists
    user = db.session.query(Users).filter_by(email=email).first()
    if user:
        return jsonify({
            'error': 'Employee already exists'
        }), 409
    #add new user
    new_user = Users(
        user_id = gen_uuid(),
        role = payload['role'],
        first_name = first_name,
        last_name = last_name,
        email = email,
        #contact = payload['contact'],
        #gender = payload['gender'],
        status = payload.get('status'),
        department = payload['dep'],
        job_title = payload['jobTitle'],
        #national_id = payload.get('nationalId'),
        joined = payload.get('joined')
    )
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
    #send email
    body = f'You have successfully been registered as an employee at Development dynamics\
        Your one time password is {password}. You is to access your account and set your preffered one.'
    subject = 'Development Dynamics registration'
    recipients = [email]
    send_email(subject, recipients, body)
    return jsonify(
        {
            'message': f'Successfully added employee {first_name, last_name}'
        }
    ), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    '''user login endpoint'''
    payload = request.get_json()
    #validate payload
    validation = _check_schema(payload, 'login')
    if validation is not True :
        current_app.logger.error(f'Validation error on login: {validation}')
        return jsonify({
            'error': 'Invalid input. Please try again'
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
    #create response
    response = make_response({
    'role': role,
    'message': 'Login successful',
    })
    #create access tokens
    identity = {
        'email': email,
        'role': role,
        'user_id': user.user_id
    }
    jwt_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    csrf_token = get_csrf_token(jwt_token)
    set_access_cookies(response, jwt_token)
    set_refresh_cookies(response, refresh_token)
    # Set a separate, readable CSRF token
    response.set_cookie(
        'csrf_token', csrf_token, domain='eazy-manage-frontend.vercel.app', httponly=False, secure=True, samesite='None'
    )
    return response, 200

@auth_bp.route('/reset_pwd', methods=['GET', 'POST'])
def reset_pwd():
    '''reset the user password'''
    args = request.args
    #validate reset action
    validation_err = _check_schema(args, 'reset_action')
    if validation_err:
        current_app.logger.error(f'Validation error on reset password: {validation_err}')
        return jsonify({
            'error': 'Invalid reset action! Please try again'
            }), 400
    action = args['action']
    payload = request.get_json()
    #send reset code
    if action == 'get_reset_code':
        #validate email
        validation_err = _check_schema(payload, 'get_reset_code')
        if validation_err:
            current_app.logger.error(f'Validation error on reset password: {validation_err}')
            return jsonify({
                'error': 'Invalid email! Please try again'
            }), 400
        email = payload['email']
        #check if user exists
        try:
            user = users.find_one({'email': email})
            if not user:
                return jsonify({
                'error': 'Invalid email! Please try again'
                }), 404
        except:
            current_app.logger.error('An error occured while querying user to reset password', exc_info=True)
            return jsonify({
                'error': 'An error occured! Please try again'
            }), 400
        #send reset code
        try:
            code = create_random_num()
            redis_client.setex(email, 5*60, code)
        except:
            current_app.logger.error('An error occured while creating the reset code', exc_info=True)
            return jsonify({
                'error': 'An error occured! Please try again'
            }), 400
        subject = 'AWAN AFRIKA resource hub password reset'
        body = f'You have requested to reset your password. Use the code below\n\
                {code}\n\
                If you did not make this request please reach out to us immediately.'
        recipients = [email]
        send_email(subject, recipients, body)
    #reset password
    else:
        validation_err = _check_schema(payload, 'reset_pwd')
        if validation_err:
            current_app.logger.error(f'Validation error on reset password: {validation_err}')
            return jsonify({
                'error': 'Invalid code! Please try again'
            }), 400
        client_code = payload['auth_code']
        email = payload['email']
        password = payload['password']
        server_code = redis_client.get(email)
        #verify code
        if server_code != client_code:
            return jsonify({
                'error': 'Invalid code! Please try again'
            }), 400
        #change password
        with mongo_client.start_session() as session:
            with session.start_transaction():
                try:
                    users.update_one({'email': email}, {'password': hash_pwd(password)})
                    session.commit_transaction()
                except:
                    session.abort_transaction()
                    current_app.logger.error('An error occured while resetting password', exc_info=True)
                    return jsonify({
                    'error': 'An error occured! Please try again'
                    }), 500
        #send confirmation email
        subject = 'AWAN AFRIKA resource hub password reset successful'
        body = 'You have successfully reset your password. If this was not you please contact us immediately'
        recipients = [email]
        send_email(subject, recipients, body)
        return jsonify(
        {
            'message': 'Password reset successful',
        }
    ), 201

@auth_bp.route('/auth_status', methods=['POST'])
@jwt_required()
def auth_status():
    '''checks the auth status'''
    payload = request.get_json()
    verified = _check_schema(payload, 'auth_status')
    if not verified:
        return jsonify({'status': 'false'}), 403
    identity = get_jwt_identity()
    role = payload['role']
    #verify admin
    if role == 'admin':
        if role != identity['role']:
            return jsonify({'status': 'false'}), 403
    return jsonify({'status': 'true'}), 200
        
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