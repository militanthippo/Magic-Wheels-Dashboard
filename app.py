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
app = dashboard.dashboard.app.server

# Register OAuth routes
register_oauth_routes(app)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
