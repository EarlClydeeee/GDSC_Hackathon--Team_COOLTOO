from app import app
import os
from werkzeug.utils import secure_filename
from flask import render_template, request

from ..services import db, cursor

@app.route('/incident', methods=["POST", "GET"])
def incident_page():
    if request.method == "POST":
        print("Form submitted!")
        form = request.form

        incident_type = form.get("incidentType")
        description = form.get("description")
        location = form.get("location")
        incident_date = form.get("incidentDate")
        full_name = form.get("fullName")
        email = form.get("email")
        contact_number = form.get("contactPhone")

        images = request.files.getlist('images')
        if not images:
            print("There are no images")

        incident_types = {
            "accident": 1,
            "emergency": 2,
            "peace": 3,
            "social": 4,
            "infra": 5,
            "behaviour": 6,
            "governance": 7
        }

        incident_type = incident_types.get(incident_type)

        try:
            query = '''
                    INSERT INTO incident_reports (full_name, email, phone_number, details, incident_type, incident_date, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    '''
            values = (full_name, email, contact_number, description, incident_type, incident_date, location)
            cursor.execute(query, values)
            report_id = cursor.lastrowid

            for image in images:
                print("uploading image....")
                if image.filename:
                    filename = secure_filename(image.filename)
                    upload_dir = os.path.join(os.getcwd(), 'app', 'uploads')
                    app.config['UPLOAD_FOLDER'] = upload_dir
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(filepath)
                    cursor.execute("INSERT INTO incident_images (report_id, image_path) VALUES (%s, %s)", (report_id, filepath))

            db.commit()

            print("Incident Report Successfully Filed")
        except Exception as e:
            print(f"Error: {e}")

    try:
        return render_template('incident-page.html', title='Submit a Complaint')
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        raise


