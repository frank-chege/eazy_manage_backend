#!/usr/bin/env python3
'''entry point to the program
creates app and runs it'''
from api.v1 import register_routes
from flask import Flask
from models.models import db
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask_mail import Mail
from log_conf import logger
from flask_talisman import Talisman
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

app = Flask(__name__)

def configure_app(app):
    '''create and configure app'''
    load_dotenv()
    app.secret_key = os.getenv('APP_KEY')

    # Set up JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_COOKIE_SECURE'] = False
    #app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    JWTManager(app)

    #serve the app over https only
    # talisman = Talisman(app, content_security_policy=None)

    CORS(app, supports_credentials=True)
    
    #setup logging
    try:
        app.logger = logger
        app.logger.info('Logging setup successfully')
    except:
        app.logger.warning(f'Logging setup failed!', exc_info=True)
        raise

    #set up database
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URL')
        print(os.getenv('MYSQL_URL'))
        app.logger.info('DataBase set up successfully')
        db.init_app(app)
        #create the database
        with app.app_context():
            db.create_all()
        app.logger.info('database set up successfully')
    except:
        app.logger.warning(f'database set up failed!', exc_info=True)
        raise

    #set up migration
    try:
        Migrate(app, db)
        app.logger.info('Migrations set up successfully')
    except:
        app.logger.warning(f'Migration set up failed!', exc_info=True)
        raise

    #register blueprints
    try:
        register_routes(app)
        app.logger.info('Blueprints registered successfully')
    except:
        app.logger.critical(f'Blueprints registration failed!', exc_info=True)
        raise
    
    #configure mail server
    try:
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        Mail(app)
        app.logger.info('Mail service setup successfully')
    except:
        app.logger.critical(f'Mail service setup failed!', exc_info=True)
        raise
    
    return app

#create the app
try:
    app = configure_app(app)
    app.logger.info('App created successfully')
except:
    app.logger.critical(f'App was not created!',  exc_info=True)
    raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #port=443, ssl_context=('cert.pem', 'key.pem')
