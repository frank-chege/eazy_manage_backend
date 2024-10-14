'''employee routes'''

from flask import (
    Blueprint,
    request
)

employees_bp = Blueprint('employees', __name__)