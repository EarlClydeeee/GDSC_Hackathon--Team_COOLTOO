from services.sql_connection import db, cursor
from datetime import datetime, timedelta
import random

def insert_test_data():
    try:
        # Sample data
        incident_types = ['emergency', 'accident', 'health', 'community', 'governance']
        locations = [
            '14.5995,120.9842',  # Manila
            '14.6091,121.0223',  # Quezon City
            '14.5176,121.0509',  # Makati
            '14.5547,121.0244',  # Mandaluyong
            '14.5378,121.0014'   # Manila Bay area
        ]
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['active', 'resolved', 'pending']
        descriptions = [
            "Traffic accident involving two vehicles",
            "Medical emergency - elderly person needs assistance",
            "Fire reported in residential building",
            "Noise complaint from neighborhood",
            "Flooding in street",
            "Power outage affecting multiple blocks",
            "Public disturbance at local park",
            "Suspicious activity reported",
            "Building code violation",
            "Water supply interruption"
        ]

        # Generate 20 sample incidents
        for i in range(20):
            days_ago = random.randint(0, 30)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute("""
                INSERT INTO incidents (
                    incident_type, description, location, status,
                    created_at, priority, assigned_to
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                random.choice(incident_types),
                random.choice(descriptions),
                random.choice(locations),
                random.choice(statuses),
                created_at,
                random.choice(priorities),
                "Admin"
            ))

        # Commit the changes
        db.commit()
        print("Test data inserted successfully!")

    except Exception as e:
        print(f"Error inserting test data: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    insert_test_data()
