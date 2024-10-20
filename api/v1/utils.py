'''utility functions'''
import bcrypt
import uuid
from flask_mail import Mail, Message
import importlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import redis
import os
from werkzeug.utils import secure_filename
from flask import current_app
import random
from flask_jwt_extended import get_jwt_identity
from .schema import task_schema
from marshmallow import ValidationError

executor = ThreadPoolExecutor() #to create a separate thread to send the email
#set redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

#async email function
def send_async_mail(app, msg: Mail):
    #send email asynchronously
    with app.app_context():
        mail = Mail(app)
        mail.send(msg)

#async email function
def send_email(subject: str, recipients: list[str], body: str):
    '''prepare to send email asynchronously with flask mail'''
    app_file = importlib.import_module('app')
    app = app_file.app
    msg = Message(subject, sender='naismart@franksolutions.tech', recipients=recipients)
    msg.body = body
    executor.submit(send_async_mail, app, msg)

#hash password
def hash_pwd(password: str)->bytes:
    '''hash the password with a salt'''
    pwd_bytes = password.encode('UTF-8')
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_pwd

#check hashed password
def check_pwd(password: str, hashed_pwd: bytes)->bool:
    '''checks whether a password is correct'''
    pwd_bytes = password.encode('UTF-8')
    return bcrypt.checkpw(pwd_bytes, hashed_pwd)

#generate uuid
def gen_uuid()->uuid:
    '''generates a uuid'''
    return str(uuid.uuid4())

#get current time
def get_cur_time():
    '''returns current time'''
    return datetime.now()

def pre_process_file(file, dir_name, username)->str:
    '''pre-process a file and store it'''
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dir_name, username + '-' + filename)
    file.save(file_path)
    return file_path

def create_random_num():
    '''creates a random password'''
    return str(random.randint(000000, 999999))

def check_auth_status(request_role)->bool:
        '''checks the auth status'''
        identity = get_jwt_identity()
        return identity.get('role') == request_role

def check_task_schema(payload: dict, activity: str):
    '''check the shema'''
    try:
        schema = task_schema(activity)
        schema.load(payload)
        return True
    except ValidationError as err:
        return {
                'error':{
                    'type': 'ValidationError',
                    'message': err.messages
                }
            }