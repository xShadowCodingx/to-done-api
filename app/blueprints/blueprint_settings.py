import datetime
from flask import Blueprint, request, jsonify, session
from uuid import uuid4
from app.extensions import db
from app.models import Settings
from app.util.decorators import login_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Get current user's settings
@settings_bp.route('/', methods=['GET'])
@login_required
def get_settings():
    settings = Settings.query.filter_by(user_public_id=session['user_public_id']).first()
    if not settings or settings.user_public_id != session['user_public_id']:
        return jsonify({'error': 'Settings not found or access denied'}), 404
    return jsonify({
        'public_id': settings.public_id,
        'user_public_id': settings.user_public_id,
        'theme': settings.theme,
        'separate_teams_todos': settings.separate_teams_todos,
        'hide_completed_todos': settings.hide_completed_todos,
        'language': settings.language,
        'timezone': settings.timezone
    })

# Update current user's settings
@settings_bp.route('/edit', methods=['PUT'])
@login_required
def edit_settings():
    settings = Settings.query.filter_by(user_public_id=session['user_public_id']).first()
    if not settings or settings.user_public_id != session['user_public_id']:
        return jsonify({'error': 'Settings not found or access denied'}), 404
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    for field in ['theme', 'separate_teams_todos', 'hide_completed_todos', 'language', 'timezone']:
        if field in data:
            setattr(settings, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Settings updated', 'public_id': settings.public_id})

# Reset current user's settings to default
@settings_bp.route('/reset', methods=['POST'])
@login_required
def reset_settings():
    settings = Settings.query.filter_by(user_public_id=session['user_public_id']).first()
    if not settings or settings.user_public_id != session['user_public_id']:
        return jsonify({'error': 'Settings not found or access denied'}), 404
    settings.theme = 'light'
    settings.separate_teams_todos = False
    settings.hide_completed_todos = False
    settings.language = 'en'
    settings.timezone = 'UTC'
    db.session.commit()
    return jsonify({'message': 'Settings reset to default', 'public_id': settings.public_id})