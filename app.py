import os
import sys
from dash import Dash
from flask import Flask

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import dashboard modules
from app.dashboard_implementation import DashboardImplementation
from app.oauth_callback import register_oauth_routes

# Create the dashboard
dashboard = DashboardImplementation()
server = dashboard.dashboard.app.server  # Store in a variable named 'server' first

# Register OAuth routes
register_oauth_routes(server)

# Create the 'app' variable that Gunicorn is looking for
app = server  # This is the key line - Gunicorn looks for this specific variable name

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
