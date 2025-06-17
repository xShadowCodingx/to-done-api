# Authentication Blueprint

from flask import Blueprint, request, jsonify, session
from app.models import User
from app.extensions import db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Username / Password is incorrect'}), 401
    session['user_public_id'] = user.public_id
    response = jsonify({'message': 'Login successful', 'public_id': user.public_id})
    return response

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_public_id', None)
    response = jsonify({'message': 'Logged out'})
    response.delete_cookie('session')
    return response