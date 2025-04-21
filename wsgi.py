import os
import sys
from flask import Flask

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the dashboard implementation directly
from app.dashboard_implementation import DashboardImplementation

# Create the dashboard instance
dashboard_impl = DashboardImplementation()

# Get the Flask server
app = dashboard_impl.dashboard.app.server

# Register OAuth routes if needed
try:
    from app.oauth_callback import register_oauth_routes
    register_oauth_routes(app)
except ImportError:
    pass

# Print debug information
print("WSGI app initialized successfully with dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
