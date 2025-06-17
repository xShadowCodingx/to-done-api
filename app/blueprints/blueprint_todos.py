import datetime
from flask import Blueprint, request, jsonify, session
from uuid import uuid4
from app.extensions import db
from app.models import TodoItem
from app.util.decorators import login_required

todos_bp = Blueprint('todos', __name__, url_prefix='/todos')

# Create a new todo item
@todos_bp.route('/create', methods=['POST'])
@login_required
def create_todo():
    data = request.json
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    now = datetime.datetime.utcnow()
    # Convert due_date to datetime if provided as a string
    due_date = data.get('due_date')
    if due_date and isinstance(due_date, str):
        try:
            due_date = datetime.datetime.fromisoformat(due_date)
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use ISO 8601 format.'}), 400
    todo = TodoItem(
        public_id=str(uuid4()),
        user_public_id=session['user_public_id'],
        title=data['title'],
        summary=data.get('summary'),
        due_date=due_date,
        completed=data.get('completed', False),
        priority=data.get('priority', 'normal'),
        assigned_to=data.get('assigned_to'),
        shared_with=data.get('shared_with'),
        created_by=session['user_public_id'],
        created_on=now,
        visibility=data.get('visibility', 'public')
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify({'message': 'Todo created', 'public_id': todo.public_id}), 201

# Get all todo items for the logged-in user, including todos assigned to any teams they are a part of
@todos_bp.route('/', methods=['GET'])
@login_required
def get_todos():
    from app.models import Team
    user_public_id = session['user_public_id']
    # Get all teams the user is a member of
    teams = Team.query.filter(Team.members.contains([user_public_id])).all()
    team_ids = [team.public_id for team in teams]
    # Query for todos owned by the user or assigned to any of their teams
    todos = TodoItem.query.filter(
        (TodoItem.user_public_id == user_public_id) |
        (TodoItem.assigned_to.in_(team_ids))
    ).all()
    # Return todos as JSON
    return jsonify([
        {
            'public_id': t.public_id,
            'title': t.title,
            'summary': t.summary,
            'due_date': t.due_date,
            'completed': t.completed,
            'priority': t.priority,
            'assigned_to': t.assigned_to,
            'shared_with': t.shared_with,
            'created_by': t.created_by,
            'created_on': t.created_on,
            'visibility': t.visibility
        } for t in todos
    ])

# Get a specific todo item by public_id
@todos_bp.route('/<public_id>', methods=['GET'])
@login_required
def get_todo(public_id):
    todo = TodoItem.query.filter_by(public_id=public_id, user_public_id=session['user_public_id']).first()
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify({
        'public_id': todo.public_id,
        'title': todo.title,
        'summary': todo.summary,
        'due_date': todo.due_date,
        'completed': todo.completed,
        'priority': todo.priority,
        'assigned_to': todo.assigned_to,
        'shared_with': todo.shared_with,
        'created_by': todo.created_by,
        'created_on': todo.created_on,
        'visibility': todo.visibility
    })

# Update a todo item
@todos_bp.route('/edit/<public_id>', methods=['PUT'])
@login_required
def edit_todo(public_id):
    todo = TodoItem.query.filter_by(public_id=public_id, user_public_id=session['user_public_id']).first()
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    for field in ['title', 'summary', 'due_date', 'completed', 'priority', 'assigned_to', 'shared_with', 'visibility']:
        if field in data:
            setattr(todo, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Todo updated', 'public_id': todo.public_id})

# Delete a todo item
@todos_bp.route('/delete/<public_id>', methods=['DELETE'])
@login_required
def delete_todo(public_id):
    todo = TodoItem.query.filter_by(public_id=public_id, user_public_id=session['user_public_id']).first()
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted', 'public_id': public_id})

# Get all todos assigned to a specific team by team public_id
@todos_bp.route('/team/<team_public_id>', methods=['GET'])
@login_required
def get_team_todos(team_public_id):
    todos = TodoItem.query.filter_by(assigned_to=team_public_id).all()
    return jsonify([
        {
            'public_id': t.public_id,
            'title': t.title,
            'summary': t.summary,
            'due_date': t.due_date,
            'completed': t.completed,
            'priority': t.priority,
            'assigned_to': t.assigned_to,
            'shared_with': t.shared_with,
            'created_by': t.created_by,
            'created_on': t.created_on,
            'visibility': t.visibility
        } for t in todos
    ])

