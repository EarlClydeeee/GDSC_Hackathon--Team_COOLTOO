from app import app
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

        try:
            query = '''
                    INSERT INTO incident_reports (full_name, email, phone_number, details, incident_type, incident_date, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    '''
            values = (full_name, email, contact_number, description, incident_type, incident_date, location)
            cursor.execute(query, values)

            db.commit()

            print("Incident Report Successfully Filed")
        except Exception as e:
            print(f"Error: {e}")

    try:
        return render_template('incident-page.html', title='Submit a Complaint')
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        raise


