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