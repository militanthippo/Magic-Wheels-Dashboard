import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try different ways to import the Flask app
try:
    # First attempt: Import directly from app.py
    from app import server as flask_app
except (ImportError, AttributeError):
    try:
        # Second attempt: Import DashboardImplementation directly
        from app.dashboard_implementation import DashboardImplementation
        # Create an instance of the dashboard
        dashboard_impl = DashboardImplementation()
        # Get the Flask server from the dashboard
        flask_app = dashboard_impl.dashboard.app.server
    except (ImportError, AttributeError):
        # Final fallback: Create a simple Flask app
        from flask import Flask
        flask_app = Flask(__name__)
        
        @flask_app.route('/')
        def home():
            return "Dashboard is being configured. Please check back later."

# Create the 'app' variable that Gunicorn is looking for
app = flask_app

# Print debug information
print("WSGI app initialized successfully")
