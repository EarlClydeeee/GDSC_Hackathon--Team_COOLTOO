from flask import Flask, render_template, request
from datetime import datetime, date, timedelta
from app import app
import calendar


def month_calendar(year, month):
    cal = calendar.Calendar(calendar.SUNDAY)
    month_days = cal.monthdayscalendar(year, month)
    return month_days

@app.route("/appointment_scheduler", methods=["GET", "POST"])
def calendar_view():
    today = date.today()
    year = request.args.get("year", default=today.year, type=int)
    month = request.args.get("month", default=today.month, type=int)

    # Handle POST actions
    if request.method == "POST":
        action = request.form.get("action")
        appt_type = request.form.get("appt_type")
        description = request.form.get("description")
        affiliation = request.form.get("affiliation")
        appt_number = request.form.get("appt_number")
        name = request.form.get("name")
        number = request.form.get("number")
        email = request.form.get("email")

        # Add logic here to create, edit, or delete appointments
        if action == "create":
            # Logic to create an appointment
            '''
            
            '''
            print(f"Creating appointment: Type: {appt_type}, Description: {description}, Affiliation: {affiliation}, Number: {appt_number}, Name: {name}, Contact: {number}, Email: {email}")
        
        elif action == "edit":
            # Logic to edit an existing appointment
            '''
            
            '''
            print(f"Editing appointment: Type: {appt_type}, Description: {description}, Affiliation: {affiliation}, Number: {appt_number}, Name: {name}, Contact: {number}, Email: {email}")
        
        elif action == "delete":
            # Logic to delete an appointment
            '''
            
            '''
            print(f"Deleting appointment for Name: {name}")

        # Optionally, redirect or render a message
        return render_template("appointment_scheduler.html", message="Appointment action processed.")

    # Get previous and next month for navigation
    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    month_days = month_calendar(year, month)
    month_name = calendar.month_name[month]

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