from functools import wraps
from flask import make_response, url_for, request, jsonify, abort
from werkzeug.utils import redirect

from .context import AuthContext

__author__ = 'Tharun M Paul (tmpaul06@gmail.com)'


def authenticate_route(f):
    """Login required decorator that checks for user in flask context"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if AuthContext.current_user_id is None:
            # Log the user out by making a POST call to logout
            # so that session, CSRF etc is cleared
            # Make a get call to login
            r = make_response(redirect(url_for('auth_bp.login',
                                               next=request.url)))
            # Clear cookies that need to be cleared
            return r
        return f(*args, **kwargs)
    return decorated_function


def authenticate_api(f):
    """Decorator for protecting API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if AuthContext.current_user_id is None:
            # Log the user out by making a POST call to logout
            # so that session, CSRF etc is cleared
            return jsonify({
                'message': 'Unauthorized'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def permissions_required(*Permission_klasses, resolver=None):
    """Decorator for enforcing given set of permissions"""
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access = True
            for Permission_klass in Permission_klasses:
                if not resolver:
                    permission = Permission_klass()
                else:
                    permission = Permission_klass(obj=resolver(kwargs))
                if not permission.check():
                    access = permission
                    break
            if access is True:
                return f(*args, **kwargs)
            else:
                return abort(403, description='{} error. You do not have permissions to perform this operation'.format(
                    access.__class__.__name__
                ))
        return decorated_function
    return wrapper



