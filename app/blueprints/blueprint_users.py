# Blueprint for users

import datetime
from flask import Blueprint, request, jsonify, session
from uuid import uuid4
from app.extensions import db
from app.models import User, Settings
from app.util.utility_functions import validate_name, validate_email, validate_password, hash_password, verify_password, encode_image_to_base64
from app.util.decorators import login_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

# This endpoint is for development purposes only and should not be used in production.
@users_bp.route('/', methods=['GET'])
def index():
    """List all users."""
    return "List of users"

# Create new user
@users_bp.route('/create', methods=['POST'])
def create_user():
    new_user_data = request.json

    # Check if new_user_data is provided
    if not new_user_data:
        return jsonify({"error": "No user data provided"}), 400

    # Validate the user data
    name_validation = validate_name(new_user_data.get('profile_name', ''))
    email_validation = validate_email(new_user_data.get('email', ''))
    password_validation = validate_password(new_user_data.get('password', ''))

    # Check if validations passed
    if name_validation is not True:
        return name_validation
    if email_validation is not True:
        return email_validation
    if password_validation is not True:
        return password_validation
    
    # Check if the user already exists
    existing_user = User.query.filter_by(email=new_user_data.get('email')).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Use current UTC time for timestamps
    now = datetime.datetime.utcnow()
    profile_picture = new_user_data.get('profile_picture')
    if profile_picture and not isinstance(profile_picture, bytes):
        profile_picture = b''

    # Create a new user instance and initial settings
    new_user = User(
        public_id=str(uuid4()),
        profile_name=new_user_data.get('profile_name'),
        email=new_user_data.get('email'),
        password=hash_password(new_user_data.get('password')),
        profile_picture=encode_image_to_base64(profile_picture) if profile_picture else None,
        last_password_change=now,
        joined_on=now,
        last_update=now,
        last_activity=now
    )

    new_settings = Settings(
        public_id=str(uuid4()),
        user_public_id=new_user.public_id,
        theme='light',
        separate_teams_todos=False,
        hide_completed_todos=False,
        language='en',
        timezone='UTC'
    )

    db.session.add_all([new_user, new_settings])
    db.session.commit()

    return jsonify({"message": "New user created!"}), 201

# Get user information by public id
@login_required
@users_bp.route('/<public_id>', methods=['GET'])
def get_user(public_id):
    if session.get('user_public_id') != public_id:
        return jsonify({'error': 'Unauthorized: You can only view your own profile.'}), 403
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'public_id': user.public_id, 'profile_name': user.profile_name})

@login_required
@users_bp.route('/edit/<public_id>', methods=['PUT'])
def edit_user(public_id):
    if session.get('user_public_id') != public_id:
        return jsonify({'error': 'Unauthorized: You can only edit your own profile.'}), 403
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'profile_name' in data:
        user.profile_name = data['profile_name']
    if 'email' in data:
        user.email = data['email']
    if 'profile_picture' in data:
        profile_picture = data['profile_picture']
        if profile_picture and not isinstance(profile_picture, bytes):
            profile_picture = b''
        user.profile_picture = encode_image_to_base64(profile_picture) if profile_picture else None
    if 'password' in data and 'new_password' in data:
        if validate_password(data['new_password']) is not True:
            return jsonify({'error': 'Invalid password format'}), 400
        if verify_password(data['password'], user.password) is not True:
            return jsonify({'error': 'Current password is incorrect'}), 400
        user.password = hash_password(data['new_password'])
        user.last_password_change = datetime.datetime.utcnow()
        user.last_update = datetime.datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'User updated', 'public_id': user.public_id})

@users_bp.route('/delete/<public_id>', methods=['DELETE'])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted', 'public_id': public_id})