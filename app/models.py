# Models for the api

from app.extensions import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BLOB, BOOLEAN, JSON, event
from sqlalchemy.engine import Engine
import sqlite3

class User(db.Model):
    """User model for the application."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    public_id = Column(String(120), unique=True, nullable=False)
    profile_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    last_password_change = Column(DateTime, default=datetime.utcnow)
    joined_on = Column(DateTime, default=datetime.utcnow)
    last_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    profile_picture = Column(BLOB, nullable=True)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
class Settings(db.Model):
    """Settings model for the application."""
    
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    public_id = Column(String(120), unique=True, nullable=False)
    user_public_id = Column(String(120), db.ForeignKey('users.public_id', ondelete='CASCADE'), nullable=False)
    theme = Column(String(50), default='light')
    separate_teams_todos = Column(BOOLEAN, default=False)
    hide_completed_todos = Column(BOOLEAN, default=False)
    language = Column(String(50), default='en')
    timezone = Column(String(50), default='UTC')
    
    user = db.relationship('User', backref=db.backref('settings', passive_deletes=True), passive_deletes=True)
    
    def __repr__(self):
        return f'<Setting {self.key} for User {self.user_id}>'

class TodoItem(db.Model):
    """TodoItem model for the application."""
    
    __tablename__ = 'todo_items'
    
    id = Column(Integer, primary_key=True)
    public_id = Column(String(120), unique=True, nullable=False)
    user_public_id = Column(String(120), db.ForeignKey('users.public_id'), nullable=False)
    visibility = Column(String(50), default='public')  # 'public', 'private', 'team'
    title = Column(String(200), nullable=False)
    summary = Column(String(500), nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed = Column(BOOLEAN, default=False)
    priority = Column(String(50), default='normal')  # 'low', 'normal', 'high'
    assigned_to = Column(String(120), nullable=True)
    shared_with = Column(JSON, nullable=True)  # List of user public IDs
    created_by = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='todo_items')
    
    def __repr__(self):
        return f'<TodoItem {self.title} for User {self.user_public_id}>'

class Team(db.Model):
    """Team model for the application."""
    
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    public_id = Column(String(120), unique=True, nullable=False)
    owner_public_id = Column(String(120), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)
    members = Column(JSON, nullable=True)  # List of user public IDs
    team_image = Column(BLOB, nullable=True)
    is_active = Column(BOOLEAN, default=True)
    deleted = Column(BOOLEAN, default=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    created_on = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Team {self.name}>'

# Ensure foreign key constraints are enforced in SQLite
# This is necessary for SQLite as it does not enforce foreign key constraints by default.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()