# This file will be used to define the main route of the application.


from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    """
    Render the index page.
    """
    return render_template('index.html', title='Home', message='Welcome to the Flask Application!')