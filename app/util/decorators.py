from functools import wraps
from flask import session, jsonify

# Decorators for the api
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_public_id' not in session:
            return jsonify({'error': 'You must be logged in to access this page.'}), 401
        return f(*args, **kwargs)
    return decorated_function