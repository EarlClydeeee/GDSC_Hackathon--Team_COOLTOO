from services.sql_connection import db, cursor

def setup_database():
    try:
        # Create incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                incident_type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                location VARCHAR(255) NOT NULL,
                status ENUM('active', 'resolved', 'pending') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                reported_by VARCHAR(255) NOT NULL,
                contact_email VARCHAR(255),
                contact_phone VARCHAR(20),
                priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                resolution_notes TEXT,
                assigned_to VARCHAR(255),
                evidence_files JSON,
                INDEX idx_incident_type (incident_type),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            )
        """)

        # Create appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                appointment_date DATETIME NOT NULL,
                client_name VARCHAR(255) NOT NULL,
                purpose VARCHAR(255) NOT NULL,
                status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                contact_email VARCHAR(255),
                contact_phone VARCHAR(20),
                notes TEXT,
                INDEX idx_appointment_date (appointment_date),
                INDEX idx_status (status)
            )
        """)

        # Commit changes
        db.commit()
        print("Database setup completed successfully!")

    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    setup_database()
