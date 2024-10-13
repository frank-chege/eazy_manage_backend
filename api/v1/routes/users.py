'''user routes'''

from flask import (
    Blueprint,
    request
)

users_bp = Blueprint('users', __name__)