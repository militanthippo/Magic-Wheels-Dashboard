"""
Token storage module for OAuth tokens in production
"""

import os
import json
import sqlite3
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('token_storage')

# Database file path
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'oauth_tokens.db')

def init_db():
    """Initialize the database"""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tokens table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY,
        token_type TEXT,
        access_token TEXT,
        refresh_token TEXT,
        expires_at REAL,
        scope TEXT,
        created_at REAL,
        updated_at REAL
    )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info(f"Initialized token database: {DB_FILE}")

def save_token(token):
    """Save token to database"""
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if token exists
    cursor.execute("SELECT id FROM tokens WHERE id = 1")
    token_exists = cursor.fetchone() is not None
    
    now = datetime.now().timestamp()
    
    if token_exists:
        # Update existing token
        cursor.execute('''
        UPDATE tokens SET
            token_type = ?,
            access_token = ?,
            refresh_token = ?,
            expires_at = ?,
            scope = ?,
            updated_at = ?
        WHERE id = 1
        ''', (
            token.get('token_type', 'Bearer'),
            token.get('access_token', ''),
            token.get('refresh_token', ''),
            token.get('expires_at', 0),
            json.dumps(token.get('scope', [])),
            now
        ))
    else:
        # Insert new token
        cursor.execute('''
        INSERT INTO tokens (
            id, token_type, access_token, refresh_token, expires_at, scope, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,
            token.get('token_type', 'Bearer'),
            token.get('access_token', ''),
            token.get('refresh_token', ''),
            token.get('expires_at', 0),
            json.dumps(token.get('scope', [])),
            now,
            now
        ))
    
    conn.commit()
    conn.close()
    
    logger.info("Token saved to database")

def load_token():
    """Load token from database"""
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get token
    cursor.execute('''
    SELECT token_type, access_token, refresh_token, expires_at, scope
    FROM tokens WHERE id = 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        logger.info("No token found in database")
        return None
    
    token_type, access_token, refresh_token, expires_at, scope = result
    
    token = {
        'token_type': token_type,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at,
        'scope': json.loads(scope) if scope else []
    }
    
    logger.info("Token loaded from database")
    return token

def delete_token():
    """Delete token from database"""
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Delete token
    cursor.execute("DELETE FROM tokens WHERE id = 1")
    
    conn.commit()
    conn.close()
    
    logger.info("Token deleted from database")
