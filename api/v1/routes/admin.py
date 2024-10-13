'''admin routes'''

from flask import (
    Blueprint,
    request
)

admin_bp = Blueprint('admin', __name__)