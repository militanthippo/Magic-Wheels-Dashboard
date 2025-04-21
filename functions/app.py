
from http.server import BaseHTTPRequestHandler
import os
import sys
import importlib.util

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the app
spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app

def handler(event, context):
    return app(event, context)
