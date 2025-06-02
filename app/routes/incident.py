from app import app
from flask import render_template, request, jsonify
from ..services import db, cursor
import json

@app.route('/incident', methods=['GET', 'POST'])
def incident_page():
    try:
        if request.method == 'POST':
            # Get form data
            incident_type = request.form.get('incidentType')
            description = request.form.get('description')
            location = request.form.get('location')
            contact_name = request.form.get('contactName')
            contact_email = request.form.get('contactEmail')
            contact_phone = request.form.get('contactPhone')
            
            # Determine priority based on incident type
            priority = 'urgent' if incident_type == 'emergency' else 'medium'
            
            # Insert into database
            query = '''
                INSERT INTO incidents (
                    incident_type, description, location, 
                    reported_by, contact_email, contact_phone, 
                    priority, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
            '''
            cursor.execute(query, (
                incident_type, description, location,
                contact_name, contact_email, contact_phone,
                priority
            ))
            db.commit()
            
            return jsonify({'success': True, 'message': 'Incident reported successfully'})
            
        return render_template('incident-page.html', title='Submit a Complaint')
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
