# This is the main entry point for the application.


from app import app
import

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))