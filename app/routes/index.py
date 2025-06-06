"""
    This file contains the main route of the application.
"""


# --- Imports and environment setup ---
from app import app
from flask import render_template


# --- Route: Home page ---
@app.route('/')
@app.route('/index')
def index():
    """
    Render the index page.
    """
    return render_template('index.html', title='Home', message='Welcome to the Flask Application!')