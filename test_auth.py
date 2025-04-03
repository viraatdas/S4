#!/usr/bin/env python3
"""
Simple script to test Google authentication with SuperTokens.
This script doesn't rely on the full FastAPI application.
"""

import requests
import json
import webbrowser
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import time

# SuperTokens configuration from environment variables
SUPERTOKENS_URI = os.environ.get("SUPERTOKENS_URI", "http://localhost:3567")
SUPERTOKENS_API_KEY = os.environ.get("SUPERTOKENS_API_KEY", "")

# Google OAuth configuration from environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
# Use the exact redirect URI that's configured in Google OAuth settings
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:3000/auth/callback/google")

# Global variable to store the authorization code
auth_code = None
auth_complete = threading.Event()

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        
        # Parse the URL and extract the authorization code
        query = parse_qs(urlparse(self.path).query)
        if 'code' in query:
            auth_code = query['code'][0]
            print(f"✅ Received authorization code: {auth_code}")
            
            # Send a success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <head>
                <title>Authentication Successful</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .success { color: green; font-size: 24px; margin-bottom: 20px; }
                    .info { margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="success">Authentication Successful!</div>
                <div class="info">You can now close this window and return to the terminal.</div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send an error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <html>
            <head>
                <title>Authentication Failed</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .error { color: red; font-size: 24px; margin-bottom: 20px; }
                    .info { margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="error">Authentication Failed</div>
                <div class="info">No authorization code received. Please try again.</div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
        
        # Signal that authentication is complete
        auth_complete.set()

def start_callback_server():
    """Start a simple HTTP server to handle the OAuth callback."""
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    print("🚀 Starting callback server on http://localhost:8080")
    
    # Run the server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server

def get_google_auth_url():
    """Generate the Google OAuth authorization URL."""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid profile email',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    # Convert params to URL query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

def exchange_code_for_tokens(code):
    """Exchange the authorization code for access and refresh tokens."""
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error exchanging code for tokens: {response.text}")
        return None

def get_user_info(access_token):
    """Get user information using the access token."""
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    response = requests.get(user_info_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error getting user info: {response.text}")
        return None

def main():
    """Main function to test Google authentication."""
    print("🔑 Testing Google Authentication with SuperTokens")
    print(f"SuperTokens URI: {SUPERTOKENS_URI}")
    print(f"Google Client ID: {GOOGLE_CLIENT_ID}")
    
    # Start the callback server
    server = start_callback_server()
    
    # Generate the authorization URL
    auth_url = get_google_auth_url()
    print(f"🌐 Opening browser to authorize: {auth_url}")
    
    # Open the browser to the authorization URL
    webbrowser.open(auth_url)
    
    # Wait for the authorization to complete
    print("⏳ Waiting for authorization...")
    auth_complete.wait(timeout=120)
    
    if auth_code:
        # Exchange the authorization code for tokens
        print("🔄 Exchanging authorization code for tokens...")
        tokens = exchange_code_for_tokens(auth_code)
        
        if tokens:
            print("✅ Successfully obtained tokens:")
            print(f"Access Token: {tokens.get('access_token')[:10]}...")
            print(f"Refresh Token: {tokens.get('refresh_token')[:10] if 'refresh_token' in tokens else 'None'}...")
            print(f"ID Token: {tokens.get('id_token')[:10]}...")
            
            # Get user information
            print("👤 Getting user information...")
            user_info = get_user_info(tokens.get('access_token'))
            
            if user_info:
                print("✅ User information:")
                print(f"Name: {user_info.get('name')}")
                print(f"Email: {user_info.get('email')}")
                print(f"Picture: {user_info.get('picture')}")
                
                # Save user info to a file
                with open('user_info.json', 'w') as f:
                    json.dump(user_info, f, indent=2)
                print("💾 User information saved to user_info.json")
            else:
                print("❌ Failed to get user information")
        else:
            print("❌ Failed to exchange authorization code for tokens")
    else:
        print("❌ No authorization code received")
    
    # Stop the server
    server.shutdown()
    print("🛑 Server stopped")

if __name__ == "__main__":
    main()
