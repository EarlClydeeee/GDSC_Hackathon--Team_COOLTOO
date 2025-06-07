"""
    This module contains the logic and routing for the appointment scheduler.
    It allows users to create, edit, and delete appointments.
    Also displays a calendar view.
"""


# --- Imports and environment setup ---
from flask import Flask, render_template, request
from datetime import datetime, date, timedelta
import random
from app import app
import calendar
from ..services import connect_to_db


# --- Helper: Generate a calendar matrix for the given month ---
def month_calendar(year, month):
    cal = calendar.Calendar(calendar.SUNDAY)
    month_days = cal.monthdayscalendar(year, month)
    return month_days

# --- Helper: Generate a unique appointment number ---
def generate_appt_number():
    year = (str(datetime.today().date()))[2:4]
    digits = str(random.randint(100000, 999999))
    return year + digits

# --- Main route: Appointment scheduler page (GET: show calendar, POST: handle actions) ---
@app.route("/appointment_scheduler", methods=["GET", "POST"])
def calendar_view():
    # --- Initialize variables for template context ---
    info = None
    message = None
    today = date.today()
    # Get year and month from query params, default to today
    year = request.args.get("year", default=today.year, type=int)
    month = request.args.get("month", default=today.month, type=int)
    # Get appointment date from form or use today
    appt_date = request.form.get("selected_date") or date(year, month, today.day)

    # --- Prepare calendar data for the template ---
    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    month_days = month_calendar(year, month)
    month_name = calendar.month_name[month]

    # --- Connect to the database ---
    db, cursor = connect_to_db()

    # --- Handle POST requests (create, edit, delete) ---
    if request.method == "POST":
        # Get form data
        action = request.form.get("action")
        appt_type = request.form.get("appt_type")
        description = request.form.get("description")
        affiliation = request.form.get("affiliation")
        appt_number = request.form.get("appt_number")
        name = request.form.get("name")
        number = request.form.get("number")
        email = request.form.get("email")

        # --- Create appointment ---
        if action == "create":
            max_retries = 20
            attempt = 0
            while attempt < max_retries:
                appt_id = generate_appt_number()
                try:
                    query = '''
                        INSERT INTO appointments (appointment_id, appointment_type, details, affiliation, full_name, contact_number, email, appointment_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    input = (appt_id, appt_type, description, affiliation, name, number, email, appt_date)
                    cursor.execute(query, input)
                    db.commit()
                    # If successful, store the appointment info
                    info = {
                        "appointment_id": appt_id,
                        "appointment_type": appt_type,
                        "details": description,
                        "affiliation": affiliation,
                        "appointment_date": appt_date,
                        "full_name": name,
                        "contact_number": number,
                        "email": email
                    }
                    message = "Appointment created successfully!"
                    break
                except Exception as e:
                    # Retry if duplicate, else break on error
                    if "Duplicate entry" in str(e).lower():
                        attempt += 1
                    else:
                        message = f"Error: {e}"
                        break
            else:
                message = "Failed to generate a unique appointment ID after multiple attempts."

        # --- Edit appointment ---
        elif action == "edit":
            try:
                check_query = '''
                    SELECT * FROM appointments
                    WHERE appointment_id = %s AND full_name = %s AND contact_number = %s AND email = %s
                '''
                cursor.execute(check_query, (appt_number, name, number, email))
                result = cursor.fetchone()
                if result:
                    update_query = '''
                        UPDATE appointments
                        SET appointment_type = %s, details = %s, affiliation = %s, appointment_date = %s
                        WHERE appointment_id = %s AND full_name = %s AND contact_number = %s AND email = %s
                    '''
                    cursor.execute(update_query, (appt_type, description, affiliation, appt_date, appt_number, name, number, email))
                    db.commit()

                    # Store the updated appointment info
                    info = {
                        "appointment_id": appt_number,
                        "appointment_type": appt_type,
                        "details": description,
                        "affiliation": affiliation,
                        "appointment_date": appt_date,
                        "full_name": name,
                        "contact_number": number,
                        "email": email
                    }
                    message = "Appointment updated successfully!"
                else:
                    message = "No matching appointment found to edit."
            except Exception as e:
                message = f"Error occurred during edit: {e}"

        # --- Delete appointment ---
        elif action == "delete":
            try:
                check_query = '''
                    SELECT * FROM appointments
                    WHERE appointment_id = %s AND full_name = %s AND contact_number = %s AND email = %s
                '''
                cursor.execute(check_query, (appt_number, name, number, email))
                result = cursor.fetchone()
                if result:
                    delete_query = '''
                        DELETE FROM appointments
                        WHERE appointment_id = %s AND full_name = %s AND contact_number = %s AND email = %s
                    '''
                    cursor.execute(delete_query, (appt_number, name, number, email))
                    db.commit()
                    # Store the deleted appointment info
                    info = {
                        "appointment_id": appt_number,
                        "full_name": name,
                        "contact_number": number,
                        "email": email
                    }
                    message = "Appointment deleted successfully!"
                else:
                    message = "No matching appointment found to delete."
            except Exception as e:
                message = f"Error occurred during delete: {e}"

        # --- Close DB and render template with all context ---
        cursor.close()
        db.close()
        return render_template(
            "appointment_scheduler.html",
            message=message,
            info=info,
            month_days=month_days,
            month=month,
            year=year,
            month_name=month_name,
            today=today,
            prev_month=prev_month,
            prev_year=prev_year,
            next_month=next_month,
            next_year=next_year,
            weekdays=list(calendar.day_abbr)
        )

    # GET request: just show the calendar
    cursor.close()
    db.close()
    return render_template(
        "appointment_scheduler.html",
        message=None,
        info=None,
        month_days=month_days,
        month=month,
        year=year,
        month_name=month_name,
        today=today,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        weekdays=list(calendar.day_abbr)
    )