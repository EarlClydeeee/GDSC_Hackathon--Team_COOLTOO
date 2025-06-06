"""
    This module contains the routing and logic for the dashboard,
    including fetching incident data, analytics, and exporting reports.
"""


# --- Imports and environment setup ---
from app import app
from flask import render_template, jsonify, request, send_file, abort
from ..services.sql_connection import connect_to_db
from datetime import datetime, date, timedelta
import csv
import io
import json
from functools import wraps
from flask_caching import Cache


# --- Configure Flask-Caching for performance ---
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# --- Helper: Get analytics data for dashboard charts ---
def get_analytics_data(incident_type='all', date_range='7d', priority='all'):
    """Helper function to get analytics data"""
    db, cursor = connect_to_db()
    try:
        # --- Priority distribution for pie/bar chart ---
        priority_query = """
            SELECT priority, COUNT(*) as count
            FROM incidents
            WHERE 1=1
        """
        params = []

        if incident_type != 'all':
            priority_query += " AND incident_type = %s"
            params.append(incident_type)

        if date_range == '24h':
            priority_query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
        elif date_range == '7d':
            priority_query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif date_range == '30d':
            priority_query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        priority_query += " GROUP BY priority"
        
        cursor.execute(priority_query, tuple(params))
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        priority_data = []
        for row in rows:
            priority_data.append(dict(zip(columns, row)))

        # --- Trend analysis for line chart ---
        trend_query = """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM incidents
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        cursor.execute(trend_query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        trend_data = []
        for row in rows:
            data = dict(zip(columns, row))
            if data['date']:
                data['date'] = data['date'].strftime('%Y-%m-%d')
            trend_data.append(data)

        cursor.close()
        db.close()
        return {
            'priorityDistribution': [d['count'] for d in priority_data],
            'trendLabels': [d['date'] for d in trend_data],
            'trendData': [d['count'] for d in trend_data]
        }

    except Exception as e:
        app.logger.error(f"Analytics Error: {str(e)}")
        return {
            'priorityDistribution': [0, 0, 0, 0],
            'trendLabels': [],
            'trendData': []
        }
    

# --- Dashboard main page: shows summary stats ---
@app.route('/dashboard')
def dashboard():
    db, cursor = connect_to_db()
    try:
        # Fetch active cases count
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM incidents 
            WHERE status = 'active'
        """)
        row = cursor.fetchone()
        active_cases = row[0] if row else 0

        # Fetch emergency reports  in the last 24 hours
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM incidents 
            WHERE incident_type = 'emergency' 
            AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        row = cursor.fetchone()
        emergency_reports = row[0] if row else 0

        cursor.close()
        db.close()

        return render_template('dashboard.html',
            active_cases=active_cases,
            emergency_reports=emergency_reports
        )
    except Exception as e:
        app.logger.error(f"Dashboard Error: {str(e)}")
        return render_template('dashboard.html', error="Unable to load dashboard data")


# --- API: Get filtered incidents and analytics (cached) ---
@app.route('/api/dashboard/incidents')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_incidents():
    db, cursor = connect_to_db()
    try:
        # --- Get filter parameters from request ---
        incident_type = request.args.get('type', 'all')
        date_range = request.args.get('dateRange', '7d')  # Default to last 7 days
        priority = request.args.get('priority', 'all')

        # --- Build base query and apply filters ---
        query = """
            SELECT id, incident_type, description, location, status, 
                   created_at, priority, assigned_to
            FROM incidents
            WHERE 1=1
        """
        params = []

        # Apply filters
        if incident_type != 'all':
            query += " AND incident_type = %s"
            params.append(incident_type)

        if priority != 'all':
            query += " AND priority = %s"
            params.append(priority)

        # --- Handle date range filter ---
        if date_range == '24h':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
        elif date_range == '7d':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif date_range == '30d':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        query += " ORDER BY created_at DESC"
        
        # --- Execute query and format results ---
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        incidents = []
        for row in rows:
            incident = dict(zip(columns, row))
            if incident['created_at']:
                incident['created_at'] = incident['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            incidents.append(incident)

        # --- Fetch analytics data for dashboard charts ---
        analytics = get_analytics_data(incident_type, date_range, priority)

        cursor.close()
        db.close()
        return jsonify({
            'incidents': incidents,
            'analytics': analytics
        })

    except Exception as e:
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({'error': 'Unable to fetch incident data'}), 500


# --- API: Export filtered incident data as CSV ---
@app.route('/api/dashboard/export')
def export_data():
    db, cursor = connect_to_db()
    try:
        # --- Get filter parameters ---
        incident_type = request.args.get('type', 'all')
        date_range = request.args.get('dateRange', '7d')
        priority = request.args.get('priority', 'all')

        # --- Build query with filters (same as get_incidents) ---
        query = """
            SELECT incident_type, description, location, status, 
                   created_at, priority, assigned_to
            FROM incidents
            WHERE 1=1
        """
        params = []

        if incident_type != 'all':
            query += " AND incident_type = %s"
            params.append(incident_type)

        if priority != 'all':
            query += " AND priority = %s"
            params.append(priority)

        if date_range == '24h':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
        elif date_range == '7d':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif date_range == '30d':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        # --- Execute query and write to CSV ---
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Incident Type', 'Description', 'Location', 'Status', 
                        'Created At', 'Priority', 'Assigned To'])
        
        # Write data rows
        for row in rows:
            incident = dict(zip(columns, row))
            writer.writerow([
                incident.get('incident_type', ''),
                incident.get('description', ''),
                incident.get('location', ''),
                incident.get('status', ''),
                incident['created_at'].strftime('%Y-%m-%d %H:%M:%S') if incident.get('created_at') else '',
                incident.get('priority', ''),
                incident.get('assigned_to', '')
            ])

        cursor.close()
        db.close()
        # --- Prepare response ---
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'incidents_report_{datetime.now().strftime("%Y%m%d")}.csv'
        )

    except Exception as e:
        app.logger.error(f"Export Error: {str(e)}")
        return jsonify({'error': 'Unable to export data'}), 500


# --- API: Get summary of incident statuses for dashboard widgets ---
@app.route('/api/dashboard/status-summary')
def get_status_summary():
    db, cursor = connect_to_db()
    try:
        query = """
            SELECT status, COUNT(*) as count
            FROM incidents
            GROUP BY status
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        summary = [{'status': row[0], 'count': row[1]} for row in rows]

        cursor.close()
        db.close()
        return jsonify(summary)

    except Exception as e:
        app.logger.error(f"Status Summary Error: {str(e)}")
        return jsonify({'error': 'Failed to fetch status summary'}), 500
    

# --- API: Get summary of incident types for dashboard widgets ---
@app.route('/api/dashboard/type-summary')
def get_type_summary():
    db, cursor = connect_to_db()
    try:
        query = """
            SELECT incident_type, COUNT(*) as count
            FROM incidents
            GROUP BY incident_type
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        summary = [{'type': row[0], 'count': row[1]} for row in rows]

        cursor.close()
        db.close()
        return jsonify(summary)

    except Exception as e:
        app.logger.error(f"Type Summary Error: {str(e)}")
        return jsonify({'error': 'Failed to fetch type summary'}), 500