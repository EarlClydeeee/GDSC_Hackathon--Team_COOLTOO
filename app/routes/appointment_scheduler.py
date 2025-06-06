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
    today = date.today()
    year = request.args.get("year", default=today.year, type=int)
    month = request.args.get("month", default=today.month, type=int)
    appt_date = date(year, month, today.day) 

    db, cursor = connect_to_db()

    # --- Handle POST actions: create, edit, delete appointments ---
    if request.method == "POST":
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

                    print(f"Appointment created successfully: {appt_id}")
                    break  # Success, exit loop

                except Exception as e:
                    if "Duplicate entry" in str(e).lower():
                        print(f"Duplicate appointment ID {appt_id}, retrying...")
                        attempt += 1
                    else:
                        print(f"Error: {e}")
                        break  # Break on other errors
            else:
                print("Failed to generate a unique appointment ID after multiple attempts.")

        # --- Edit appointment ---
        elif action == "edit":
            # Logic to edit an existing appointment
            try:
                # Check if an appointment exists with the given number, name, number, and email
                check_query = '''
                    SELECT * FROM appointments
                    WHERE appointment_number = %s AND full_name = %s AND contact_number = %s AND email = %s
                '''
                cursor.execute(check_query, (appt_number, name, number, email))
                result = cursor.fetchone()
                if result:
                    # Update the type, description, and affiliation
                    update_query = '''
                        UPDATE appointments
                        SET appointment_type = %s, details = %s, affiliation = %s
                        WHERE appointment_number = %s AND full_name = %s AND contact_number = %s AND email = %s
                    '''
                    cursor.execute(update_query, (appt_type, description, affiliation, appt_number, name, number, email))
                    db.commit()
                    print(f"Appointment {appt_number} updated for {name}.")
                else:
                    print("No matching appointment found to edit.")
            except Exception as e:
                print("Error occurred during edit:", e)
        
        # --- Delete appointment ---
        elif action == "delete":
            # Logic to delete an existing appointment 
            try:
                # Check if an appointment exists with the given info
                check_query = '''
                    SELECT * FROM appointments
                    WHERE appointment_number = %s AND full_name = %s AND contact_number = %s AND email = %s
                '''
                cursor.execute(check_query, (appt_number, name, number, email))
                result = cursor.fetchone()
                if result:
                    # Delete the appointment
                    delete_query = '''
                        DELETE FROM appointments
                        WHERE appointment_number = %s AND full_name = %s AND contact_number = %s AND email = %s
                    '''
                    cursor.execute(delete_query, (appt_number, name, number, email))
                    db.commit()
                    print(f"Appointment {appt_number} deleted for {name}.")
                else:
                    print("No matching appointment found to delete.")
            except Exception as e:
                print("Error occurred during delete:", e)

        cursor.close()
        db.close()
        # Redirect or render a message
        return render_template("appointment_scheduler.html", message="Appointment action processed.")

    # --- Prepare calendar navigation and data for GET requests ---
    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    month_days = month_calendar(year, month)
    month_name = calendar.month_name[month]

    cursor.close()
    db.close()
    return render_template(
        "appointment_scheduler.html",
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