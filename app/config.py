# Configuration for the api

import os

cwd = os.getcwd()

class Config:
    """Base configuration class."""
    print(cwd + "/app/data/todone.db")
    
    # Flask settings
    TESTING = True
    SECRET_KEY = 'NotASecretKey'

    # Database settings
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + cwd + "/app/data/todone.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie settings
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Be sure to set this to True in production with HTTPS