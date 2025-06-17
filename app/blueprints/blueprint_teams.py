import datetime
from flask import Blueprint, request, jsonify, session
from uuid import uuid4
from app.extensions import db
from app.models import Team
from app.util.decorators import login_required

teams_bp = Blueprint('teams', __name__, url_prefix='/teams')

# Create a new team
@teams_bp.route('/create', methods=['POST'])
@login_required
def create_team():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Team name is required'}), 400
    now = datetime.datetime.utcnow()
    team = Team(
        public_id=str(uuid4()),
        owner_public_id=session['user_public_id'],
        name=data['name'],
        description=data.get('description'),
        members=data.get('members', [session['user_public_id']]),
        team_image=data.get('team_image'),
        is_active=True,
        deleted=False,
        last_activity=now,
        created_on=now
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team created', 'public_id': team.public_id}), 201

# Get all teams for the logged-in user (where user is a member)
@teams_bp.route('/', methods=['GET'])
@login_required
def get_teams():
    teams = Team.query.filter(Team.members.contains([session['user_public_id']])).all()
    return jsonify([
        {
            'public_id': t.public_id,
            'name': t.name,
            'description': t.description,
            'members': t.members,
            'team_image': t.team_image,
            'is_active': t.is_active,
            'deleted': t.deleted,
            'last_activity': t.last_activity,
            'created_on': t.created_on
        } for t in teams
    ])

# Get a specific team by public_id
@teams_bp.route('/<public_id>', methods=['GET'])
@login_required
def get_team(public_id):
    team = Team.query.filter_by(public_id=public_id).first()
    if not team or session['user_public_id'] not in (team.members or []):
        return jsonify({'error': 'Team not found or access denied'}), 404
    return jsonify({
        'public_id': team.public_id,
        'name': team.name,
        'description': team.description,
        'members': team.members,
        'team_image': team.team_image,
        'is_active': team.is_active,
        'deleted': team.deleted,
        'last_activity': team.last_activity,
        'created_on': team.created_on
    })

# Update a team
@teams_bp.route('/edit/<public_id>', methods=['PUT'])
@login_required
def edit_team(public_id):
    team = Team.query.filter_by(public_id=public_id).first()
    if not team or session['user_public_id'] != team.owner_public_id:
        return jsonify({'error': 'Team not found or you are not the owner'}), 403
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    for field in ['name', 'description', 'members', 'team_image', 'is_active', 'deleted']:
        if field in data:
            setattr(team, field, data[field])
    team.last_activity = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Team updated', 'public_id': team.public_id})

# Delete a team
@teams_bp.route('/delete/<public_id>', methods=['DELETE'])
@login_required
def delete_team(public_id):
    team = Team.query.filter_by(public_id=public_id).first()
    if not team or session['user_public_id'] != team.owner_public_id:
        return jsonify({'error': 'Team not found or you are not the owner'}), 403
    db.session.delete(team)
    db.session.commit()
    return jsonify({'message': 'Team deleted', 'public_id': public_id})

# Invite a member to a team by profile name
@teams_bp.route('/invite/<team_name>', methods=['POST'])
@login_required
def invite_member(team_name):
    from app.models import User
    team = Team.query.filter_by(name=team_name).first()
    if not team or session['user_public_id'] != team.owner_public_id:
        return jsonify({'error': 'Team not found or you are not the owner'}), 403
    data = request.json
    if not data or 'profile_name' not in data:
        return jsonify({'error': 'Profile name is required'}), 400
    user = User.query.filter_by(profile_name=data['profile_name']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.public_id in (team.members or []):
        return jsonify({'error': 'User is already a member'}), 400
    members = team.members or []
    members.append(user.public_id)
    team.members = members
    team.last_activity = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify({'message': f"User '{user.profile_name}' invited to team.", 'team_name': team.name, 'user_public_id': user.public_id})