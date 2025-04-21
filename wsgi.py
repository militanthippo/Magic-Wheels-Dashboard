import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from app.py
from app import dashboard

# Create the 'app' variable that Gunicorn is looking for
app = dashboard.dashboard.app.server
