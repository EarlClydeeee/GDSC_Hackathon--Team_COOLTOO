"""
    This module contains the routing and logic for the page that lists incident reports.
    It retrieves urgent and common reports from the database and renders them in a template.
"""


# --- Imports and environment setup ---
from app import app
from flask import render_template
from app.services import connect_to_db


# --- Route: List all incident reports, grouped by urgency ---
@app.route('/reports_list')
def reports_list():
    db, cursor = connect_to_db()

    # --- Query for urgent incident reports ---
    urgent_query = """
        SELECT 
            ir.unique_report_id, ir.report_status, ir.location, ir.incident_date, ir.details,
            img.image_path, ir.full_name, ir.email, ir.phone_number
        FROM incident_reports ir
        LEFT JOIN incident_images img ON ir.report_id = img.image_id
        WHERE ir.gravity = 'urgent'
    """
    cursor.execute(urgent_query)
    urgent_reports = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    # --- Query for common (non-urgent) incident reports ---
    common_query = """
        SELECT 
            ir.unique_report_id, ir.report_status, ir.location, ir.incident_date, ir.details,
            img.image_path, ir.full_name, ir.email, ir.phone_number
        FROM incident_reports ir
        LEFT JOIN incident_images img ON ir.report_id = img.image_id
        WHERE ir.gravity = 'common'
    """
    cursor.execute(common_query)
    common_reports = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    db.close()

    # --- Render the reports list template with both urgent and common reports ---
    return render_template(
        'reports_list.html',
        title="Incident Reports",
        urgent_reports=urgent_reports,
        common_reports=common_reports
    )