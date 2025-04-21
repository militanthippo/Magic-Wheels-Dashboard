"""
OAuth callback handler for the web application
"""

from flask import Blueprint, request, redirect, url_for, session, current_app
import os
import sys
import logging

# Import the OAuth client
from app.oauth_client import GoHighLevelOAuthClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oauth_callback')

# Create a Blueprint for the OAuth routes
oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/callback')
def callback():
    """Handle the OAuth callback"""
    # Get the authorization response from the request
    authorization_response = request.url
    
    # Get OAuth credentials from environment
    client_id = os.environ.get('GHL_CLIENT_ID')
    client_secret = os.environ.get('GHL_CLIENT_SECRET')
    redirect_uri = os.environ.get('GHL_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        logger.error("Missing OAuth credentials")
        return "Error: Missing OAuth credentials", 500
    
    # Create the OAuth client
    oauth_client = GoHighLevelOAuthClient(client_id, client_secret, redirect_uri)
    
    # Fetch the token
    token = oauth_client.fetch_token(authorization_response)
    
    if not token:
        logger.error("Failed to fetch token")
        return "Error: Failed to fetch token", 500
    
    # Redirect to the dashboard
    return redirect('/')

@oauth_bp.route('/authorize')
def authorize():
    """Initiate the OAuth flow"""
    # Get OAuth credentials from environment
    client_id = os.environ.get('GHL_CLIENT_ID')
    client_secret = os.environ.get('GHL_CLIENT_SECRET')
    redirect_uri = os.environ.get('GHL_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        logger.error("Missing OAuth credentials")
        return "Error: Missing OAuth credentials", 500
    
    # Create the OAuth client
    oauth_client = GoHighLevelOAuthClient(client_id, client_secret, redirect_uri)
    
    # Get the authorization URL
    authorization_url, state = oauth_client.get_authorization_url()
    
    # Redirect to the authorization URL
    return redirect(authorization_url)

def register_oauth_routes(app):
    """Register the OAuth routes with the Flask app"""
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
