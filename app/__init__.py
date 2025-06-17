# Main application factory for the api

from flask import Flask
from app.extensions import db

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Create a configuration object
    app.config.from_object('app.config.Config')

    # Initialize extensions, blueprints, etc.
    with app.app_context():
        
        # Initialize the database and import models
        from app.models import User, Team, TodoItem, Settings
        db.init_app(app)
        db.create_all()

        # Register blueprints
        from app.blueprints.blueprint_users import users_bp
        app.register_blueprint(users_bp)
        from app.blueprints.blueprint_authentication import auth_bp
        app.register_blueprint(auth_bp)
        from app.blueprints.blueprint_teams import teams_bp
        app.register_blueprint(teams_bp)
        from app.blueprints.blueprint_todos import todos_bp
        app.register_blueprint(todos_bp)
        from app.blueprints.blueprint_settings import settings_bp
        app.register_blueprint(settings_bp)

    return app