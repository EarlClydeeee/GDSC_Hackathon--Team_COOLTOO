"""
    This module handles the update and search functionality for incident reports.
    It allows users to update the status of their reports, search for existing reports,
    and view details of specific reports based on their user role (admin or reporter).
"""


# --- Imports and environment setup ---
from app import app 
from flask import request, render_template
from app.services import connect_to_db
from datetime import datetime
import random
import os


# --- Helper: Generate a unique number for incident reports ---
def generate_unique_number():
    year = (str(datetime.today().date()))[2:4]
    digits = str(random.randint(100000, 999999))
    return year + digits

# --- Get admin/official user ID from environment ---
ADMIN_USER_ID = os.getenv("ADMIN_ID")

# --- Route: Update or search incident reports (GET: show form, POST: handle actions) ---
@app.route('/update_incident', methods=["GET", "POST"])
@app.route('/update_incident_report', methods=["GET", "POST"])
def update_incident_report():
    db, cursor = connect_to_db()
    report = None
    user_role = None
    user_id = None
    message = None

    if request.method == "POST":
        unique_id = request.form.get("unique_id") or request.form.get("unique_report_id")
        user_id = request.form.get("user_id")
        action = request.form.get("action")

        # --- 1. If updating status ---
        if action and unique_id and user_id:
            try:
                # Fetch current status and user_id for validation
                if str(user_id).strip() == str(ADMIN_USER_ID).strip():
                    # Admin: fetch by unique_report_id only
                    cursor.execute(
                        "SELECT report_status, user_id FROM incident_reports WHERE unique_report_id = %s",
                        (unique_id,)
                    )
                else:
                    # Reporter: fetch by both
                    cursor.execute(
                        "SELECT report_status, user_id FROM incident_reports WHERE unique_report_id = %s AND user_id = %s",
                        (unique_id, user_id)
                    )
                current = cursor.fetchone()
            
                if not current:
                    message = "Report not found."
                else:
                    current_status, report_user_id = current
                    # Admin can mark as processed anytime
                    if action == "processed" and str(user_id).strip() == str(ADMIN_USER_ID).strip():
                        cursor.execute(
                            "UPDATE incident_reports SET report_status = 'Processed' WHERE unique_report_id = %s",
                            (unique_id,)
                        )
                        db.commit()
                        message = "Report marked as Processed."
                    # Reporter can only update if already processed
                    elif action in ["resolved", "unresolved"] and str(user_id).strip() == str(report_user_id).strip():
                        if current_status == "Processed":
                            new_status = "Resolved" if action == "resolved" else "Unresolved"
                            cursor.execute(
                                "UPDATE incident_reports SET report_status = %s WHERE unique_report_id = %s",
                                (new_status, unique_id)
                            )
                            db.commit()
                            message = f"Report marked as {new_status}."
                        else:
                            message = "You can only update status after it has been processed by admin."
                    else:
                        message = "You are not authorized to perform this action."

                # Fetch updated report for display (use same logic as above)
                if str(user_id).strip() == str(ADMIN_USER_ID).strip():
                    cursor.execute(
                        "SELECT unique_report_id, incident_type, details, location, report_status, user_id, full_name, email, phone_number FROM incident_reports WHERE unique_report_id = %s",
                        (unique_id,)
                    )
                else:
                    cursor.execute(
                        "SELECT unique_report_id, incident_type, details, location, report_status, user_id, full_name, email, phone_number FROM incident_reports WHERE unique_report_id = %s AND user_id = %s",
                        (unique_id, user_id)
                    )
                result = cursor.fetchone()

                if result:
                    columns = [desc[0] for desc in cursor.description]
                    report = dict(zip(columns, result))
                    if str(user_id).strip() == str(ADMIN_USER_ID).strip():
                        user_role = "admin"
                    elif str(user_id).strip() == str(report["user_id"]).strip():
                        user_role = "reporter"
                    else:
                        user_role = "other"
            except Exception as e:
                return f"Error updating incident report: {e}"

        # --- 2. If searching for a report ---
        elif unique_id and user_id:
            try:
                if str(user_id).strip() == str(ADMIN_USER_ID).strip():
                    # Admin can search by unique_report_id only
                    query = '''
                        SELECT unique_report_id, incident_type, details, location, report_status, user_id, full_name, email, phone_number
                        FROM incident_reports
                        WHERE unique_report_id = %s
                    '''
                    cursor.execute(query, (unique_id,))
                else:
                    # Normal user must match both
                    query = '''
                        SELECT unique_report_id, incident_type, details, location, report_status, user_id, full_name, email, phone_number
                        FROM incident_reports
                        WHERE unique_report_id = %s AND user_id = %s
                    '''
                    cursor.execute(query, (unique_id, user_id))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    report = dict(zip(columns, result))
                    if str(user_id) == str(ADMIN_USER_ID):
                        user_role = "admin"
                    elif str(user_id) == str(report["user_id"]):
                        user_role = "reporter"
                    else:
                        user_role = "other"
                else:
                    report = None
            except Exception as e:
                return f"Error updating incident report: {e}"

    cursor.close()
    db.close()

    # --- Render the update incident report page with results and messages ---
    return render_template(
        'update_incident_report.html',
        title="Update Incident Report",
        report=report,
        user_role=user_role,
        user_id=user_id,
        message=message
    )