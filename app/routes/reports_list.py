from app import app
from flask import render_template
from app.services import connect_to_db

@app.route('/reports_list')
def reports_list():
    db, cursor = connect_to_db()
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
    return render_template(
        'reports_list.html',
        title="Incident Reports",
        urgent_reports=urgent_reports,
        common_reports=common_reports
    )