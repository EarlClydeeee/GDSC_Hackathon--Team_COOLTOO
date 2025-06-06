"""
    This module is used to set up the database schema for the incident reporting application.
    It reads the SQL schema from a file and executes it to create the necessary tables.
"""


from services.sql_connection import db, cursor
import os


def setup_database():
    try:
        # Read and execute the SQL schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema', 'incidents.sql')
        with open(schema_path, 'r') as f:
            sql_schema = f.read()
            
        # Split and execute each statement
        for statement in sql_schema.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        db.commit()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    setup_database()
