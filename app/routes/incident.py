from app import app
from flask import render_template, request

@app.route('/incident')
def incident_page():
    try:
        return render_template('incident-page.html', title='Submit a Complaint')
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        raise