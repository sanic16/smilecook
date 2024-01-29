from functools import wraps
from flask_jwt_extended import get_jwt_identity
from models.user import User
from http import HTTPStatus

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user).first()
        if not user or not user.is_admin:
            return {'message': 'Admin required'}, HTTPStatus.FORBIDDEN
        return fn(*args, **kwargs)
    return wrapper