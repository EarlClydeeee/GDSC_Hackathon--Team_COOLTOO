from app import app
import os
from werkzeug.utils import secure_filename
from flask import render_template, request
from ..services import db, cursor
import random
from datetime import datetime

# Function to generate a unique number for incident reports
def generate_report_id():
    year = str(datetime.today().year)[2:]
    digits = str(random.randint(100000, 999999))
    return f"R{year}{digits}"

# Function to generate a user ID based on full name and email
def generate_user_id(full_name, email):
    # Simple hash for demo; replace with real user auth in production
    return f"U{abs(hash(full_name + email)) % 1000000}"

# Function to map incident type string to ID
def map_incident_type_to_id(incident_type_str):
    mapping = {
        "accident": 1,
        "emergency & disaster": 2,
        "peace & order": 3,
        "health & social services": 4,
        "infrastructure & utilities": 5,
        "public behavior & community concern": 6,
        "governance & transparency": 7
    }
    if incident_type_str:
        return mapping.get(incident_type_str.strip().lower())
    return None

# This file defines the route for submitting incident reports in a barangay system
@app.route('/incident', methods=["POST", "GET"])
def incident_page():
    report_info = None

    if request.method == "POST":
        form = request.form 
        incident_type_str = form.get("incidentType")
        incident_type = map_incident_type_to_id(incident_type_str)
        description = form.get("description")
        location = form.get("location")
        incident_date = form.get("incidentDate")
        full_name = form.get("fullName")
        email = form.get("email")
        contact_number = form.get("contactPhone")

        # Generate IDs and status
        unique_report_id = generate_report_id()
        user_id = generate_user_id(full_name, email)
        status = "Pending"

        # Validate required fields
        if incident_type is None:
            print(f"Invalid incident type: {incident_type_str}")
            return render_template('incident-page.html', title='Submit a Complaint', report_info=None)
          
        # Validate if there are images submitted
        images = request.files.getlist('images')
        if not images:
            print("There are no images")

        try:
            query = '''
                INSERT INTO incident_reports (unique_report_id, user_id, full_name, email, phone_number, details, incident_type, incident_date, location, report_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            values = (unique_report_id, user_id, full_name, email, contact_number, description, incident_type, incident_date, location, status)
            print("Attempting to insert:", values)
            cursor.execute(query, values)
            
            report_index = cursor.lastrowid  # This is the auto-increment primary key

            for image in images:
                print("uploading image....")
                if image.filename:
                    filename = secure_filename(image.filename)
                    upload_dir = os.path.join(os.getcwd(), 'app', 'uploads')
                    app.config['UPLOAD_FOLDER'] = upload_dir
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(filepath)

                    relative_path = os.path.join('uploads', filename)
                    cursor.execute("INSERT INTO incident_images (report_id, image_path) VALUES (%s, %s)", (report_index, relative_path))

            db.commit()
            print("Insert committed")
            print("Incident Report Successfully Filed")

            # Pass info to template for display
            report_info = {
                "unique_report_id": unique_report_id,
                "user_id": user_id,
                "status": status
            }
        except Exception as e:
            print(f"Error: {e}")

    return render_template('incident-page.html', title='Submit a Complaint', report_info=report_info)


