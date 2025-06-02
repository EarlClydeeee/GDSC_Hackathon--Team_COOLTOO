from app import app 
from flask import request, render_template
from app.services import db, cursor
from datetime import datetime
import random
import os

# Function to generate a unique number for incident reports
def generate_unique_number():
    year = (str(datetime.today().date()))[2:4]
    digits = str(random.randint(100000, 999999))
    return year + digits

# Admin/official user ID 
ADMIN_USER_ID = os.getenv("ADMIN_ID")

@app.route("/update_incident_report", methods=["GET", "POST"])
def update_incident_report():
    if request.method == "POST":
        unique_id = request.form.get("unique_id")
        user_id = request.form.get("user_id")

        # Search for the incident report by unique_id and user_id
        try:
            query = '''
            SELECT incident_id, incident_type, description, location, date_time, status
            FROM incidents
            WHERE unique_id = %s AND user_id = %s
        '''
        except Exception as e:
            return f"Error updating incident report: {e}"
        
    return "Invalid request method."


