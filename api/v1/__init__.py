'''initialises the package and registers the flask blueprints'''
from .routes.auth import auth_bp
from .routes.admin import admin_bp
from .routes.users import users_bp

def register_routes(app):
    #registers the routes from the blueprints
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(users_bp, url_prefix='/api/v1/authors')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')