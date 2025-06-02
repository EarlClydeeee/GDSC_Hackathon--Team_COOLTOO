from app import app
from flask import render_template, jsonify, request, send_file, abort
from ..services.sql_connection import db, cursor
from datetime import datetime, date, timedelta
import csv
import io
import json
from functools import wraps
from flask_caching import Cache

# Configure Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/dashboard')
def dashboard():
    try:
        # Fetch initial data for the dashboard
        # Fetch active cases
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM incidents 
            WHERE status = 'active'
        """)
        result = cursor.fetchone()
        active_cases = result['count'] if result else 0

        # Fetch emergency reports
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM incidents 
            WHERE incident_type = 'emergency' 
            AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        result = cursor.fetchone()
        emergency_reports = result['count'] if result else 0

        return render_template('dashboard.html',
            active_cases=active_cases,
            emergency_reports=emergency_reports
        )
    except Exception as e:
        app.logger.error(f"Dashboard Error: {str(e)}")
        return render_template('dashboard.html', error="Unable to load dashboard data")

@app.route('/api/dashboard/incidents')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_incidents():
    try:
        # Get filter parameters
        incident_type = request.args.get('type', 'all')
        date_range = request.args.get('dateRange', '7d')  # Default to last 7 days
        priority = request.args.get('priority', 'all')

        # Build base query
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

        # Handle date range
        if date_range == '24h':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
        elif date_range == '7d':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif date_range == '30d':
            query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

        query += " ORDER BY created_at DESC"
        
        # Execute query
        cursor.execute(query, tuple(params))
        incidents = cursor.fetchall()

        # Fetch analytics data
        analytics = get_analytics_data(incident_type, date_range, priority)

        return jsonify({
            'incidents': incidents,
            'analytics': analytics
        })

    except Exception as e:
        app.logger.error(f"API Error: {str(e)}")
        return jsonify({'error': 'Unable to fetch incident data'}), 500

@app.route('/api/dashboard/export')
def export_data():
    try:
        # Get filter parameters
        incident_type = request.args.get('type', 'all')
        date_range = request.args.get('dateRange', '7d')
        priority = request.args.get('priority', 'all')

        # Build query with filters (similar to get_incidents)
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

        cursor.execute(query, tuple(params))
        incidents = cursor.fetchall()

        # Create CSV file
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Incident Type', 'Description', 'Location', 'Status', 
                        'Created At', 'Priority', 'Assigned To'])
        
        # Write data
        for incident in incidents:
            writer.writerow([
                incident['incident_type'],
                incident['description'],
                incident['location'],
                incident['status'],
                incident['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                incident['priority'],
                incident['assigned_to']
            ])

        # Prepare response
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

def get_analytics_data(incident_type='all', date_range='7d', priority='all'):
    """Helper function to get analytics data"""
    try:
        # Priority distribution
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
        priority_data = cursor.fetchall()

        # Trend analysis
        trend_query = """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM incidents
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        cursor.execute(trend_query)
        trend_data = cursor.fetchall()

        return {
            'priorityDistribution': [d['count'] for d in priority_data],
            'trendLabels': [d['date'].strftime('%Y-%m-%d') for d in trend_data],
            'trendData': [d['count'] for d in trend_data]
        }

    except Exception as e:
        app.logger.error(f"Analytics Error: {str(e)}")
        return {
            'priorityDistribution': [0, 0, 0, 0],
            'trendLabels': [],
            'trendData': []
        }
