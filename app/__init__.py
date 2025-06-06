"""
    This file is for initializing the Flask application.
"""


from flask import Flask

# Create a Flask application instance
app = Flask(__name__)

# Import routes after creating the app instance to avoid circular imports
from app.routes import *