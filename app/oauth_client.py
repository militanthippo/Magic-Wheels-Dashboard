"""
OAuth 2.0 client for GoHighLevel API v2
"""

import os
import json
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import logging
from datetime import datetime, timedelta

# Import token storage for production
from app.token_storage import save_token, load_token, delete_token



# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'oauth.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('oauth_client')

class GoHighLevelOAuthClient:
    """OAuth 2.0 client for GoHighLevel API v2"""
    
    def __init__(self, client_id, client_secret, redirect_uri, token_file=None):
        """
        Initialize the OAuth client
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            token_file: File to store the token (default: None)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_file = token_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'oauth_token.json'
        )
        self.token = self._load_token()
        self.base_url = "https://services.leadconnectorhq.com"
        self.oauth_url = "https://marketplace.gohighlevel.com/oauth/authorize"
        self.token_url = "https://services.leadconnectorhq.com/oauth/token"
        
        # Create the OAuth session
        self.session = self._create_session()
    
    def _load_token(self):
        """Load token from storage"""
        return load_token()
    
    def _save_token(self, token):
        """Save token to storage"""
        save_token(token)
    
    def _create_session(self):
        """Create OAuth session"""
        if self.token:
            session = OAuth2Session(
                client_id=self.client_id,
                token=self.token,
                auto_refresh_url=self.token_url,
                auto_refresh_kwargs={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                },
                token_updater=self._save_token
            )
            return session
        
        # No token, create a new session
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=['locations.readonly', 'opportunities.readonly', 'contacts.readonly']
        )
        return session
    
    def get_authorization_url(self):
        """Get authorization URL for user to authorize the application"""
        authorization_url, state = self.session.authorization_url(self.oauth_url)
        return authorization_url, state
    
    def fetch_token(self, authorization_response):
        """Fetch token using authorization response"""
        try:
            token = self.session.fetch_token(
                token_url=self.token_url,
                authorization_response=authorization_response,
                client_secret=self.client_secret
            )
            self._save_token(token)
            self.token = token
            self.session = self._create_session()
            logger.info("Successfully fetched token")
            return token
        except Exception as e:
            logger.error(f"Error fetching token: {e}")
            return None
    
    def refresh_token(self):
        """Refresh the token"""
        if not self.token:
            logger.error("No token to refresh")
            return None
        
        try:
            token = self.session.refresh_token(
                token_url=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self._save_token(token)
            self.token = token
            logger.info("Successfully refreshed token")
            return token
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    def is_token_valid(self):
        """Check if token is valid"""
        if not self.token:
            return False
        
        # Check if token is expired
        expires_at = self.token.get('expires_at')
        if not expires_at:
            return False
        
        # Add buffer time to ensure token is still valid
        buffer_time = 300  # 5 minutes
        return datetime.now().timestamp() < expires_at - buffer_time
    
    def get(self, endpoint, params=None):
        """Make a GET request to the API"""
        if not self.is_token_valid():
            logger.info("Token is invalid or expired, refreshing")
            if not self.refresh_token():
                logger.error("Failed to refresh token")
                return None
        
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error making GET request to {url}: {e}")
            return None
    
    def post(self, endpoint, data=None, json_data=None):
        """Make a POST request to the API"""
        if not self.is_token_valid():
            logger.info("Token is invalid or expired, refreshing")
            if not self.refresh_token():
                logger.error("Failed to refresh token")
                return None
        
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, data=data, json=json_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error making POST request to {url}: {e}")
            return None
    
    def get_locations(self):
        """Get all locations (sub-accounts)"""
        return self.get("/locations/v2")
    
    def get_location(self, location_id):
        """Get a specific location (sub-account)"""
        return self.get(f"/locations/v2/{location_id}")
    
    def get_opportunities(self, location_id, pipeline_id=None, stage_id=None, start_date=None, end_date=None):
        """Get opportunities for a location"""
        params = {}
        if pipeline_id:
            params['pipelineId'] = pipeline_id
        if stage_id:
            params['stageId'] = stage_id
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        return self.get(f"/locations/{location_id}/opportunities/v2", params=params)
    
    def get_pipelines(self, location_id):
        """Get pipelines for a location"""
        return self.get(f"/locations/{location_id}/pipelines/v2")
    
    def get_pipeline_stages(self, location_id, pipeline_id):
        """Get stages for a pipeline"""
        return self.get(f"/locations/{location_id}/pipelines/{pipeline_id}/stages/v2")
    
    def get_contacts(self, location_id, start_date=None, end_date=None):
        """Get contacts for a location"""
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        return self.get(f"/locations/{location_id}/contacts/v2", params=params)


# Example usage
if __name__ == "__main__":
    import sys
    
    # Get credentials from environment or command line
    client_id = os.environ.get('GHL_CLIENT_ID') or (sys.argv[1] if len(sys.argv) > 1 else None)
    client_secret = os.environ.get('GHL_CLIENT_SECRET') or (sys.argv[2] if len(sys.argv) > 2 else None)
    redirect_uri = os.environ.get('GHL_REDIRECT_URI') or (sys.argv[3] if len(sys.argv) > 3 else None)
    
    if not all([client_id, client_secret, redirect_uri]):
        print("Usage: python oauth_client.py <client_id> <client_secret> <redirect_uri>")
        print("Or set environment variables: GHL_CLIENT_ID, GHL_CLIENT_SECRET, GHL_REDIRECT_URI")
        sys.exit(1)
    
    # Create the OAuth client
    client = GoHighLevelOAuthClient(client_id, client_secret, redirect_uri)
    
    # Check if we have a valid token
    if not client.is_token_valid():
        # Get authorization URL
        auth_url, state = client.get_authorization_url()
        print(f"Please go to this URL to authorize the application: {auth_url}")
        
        # Get authorization response
        auth_response = input("Enter the full callback URL: ")
        
        # Fetch token
        token = client.fetch_token(auth_response)
        if not token:
            print("Failed to fetch token")
            sys.exit(1)
    
    # Get locations
    locations = client.get_locations()
    print(f"Locations: {json.dumps(locations, indent=2)}")
