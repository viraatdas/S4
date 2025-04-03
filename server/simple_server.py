#!/usr/bin/env python3
"""
Simple FastAPI server for S4 that doesn't rely on problematic dependencies.
This server provides basic API endpoints with API key authentication and SuperTokens integration.
"""

import os
import json
import logging
import uuid
import requests
import random
import boto3
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, RedirectResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="S4 - Smart S3 Storage Service",
    description="A smart storage service that combines S3 with semantic search capabilities",
    version="0.1.0",
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", "Authorization", "X-API-Key", 
        "Access-Control-Allow-Origin", "Access-Control-Allow-Credentials",
        "fdi-version", "st-auth-mode", "rid", "anti-csrf",
        "accept", "origin", "referer", "user-agent"
    ],
    expose_headers=["Content-Type", "Authorization", "anti-csrf"],
    max_age=86400  # Cache preflight requests for 24 hours
)

# SuperTokens configuration from environment variables
SUPERTOKENS_URI = os.environ.get("SUPERTOKENS_URI", "http://localhost:3567")
SUPERTOKENS_API_KEY = os.environ.get("SUPERTOKENS_API_KEY", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
# Default redirect URI, but we'll also accept the one provided in the request
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:3000/auth/callback/google")

# SuperTokens middleware to handle auth requests
class SuperTokensMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Handle OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            logging.info(f"Handling OPTIONS request for: {path}")
            headers = {
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-API-Key, Access-Control-Allow-Origin, Access-Control-Allow-Credentials, fdi-version, st-auth-mode, rid, anti-csrf, accept, origin, referer, user-agent",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
                "Access-Control-Expose-Headers": "Content-Type, Authorization, anti-csrf"
            }
            return JSONResponse(content={}, headers=headers)
        
        # Forward auth requests to SuperTokens
        if path.startswith("/auth/"):
            logging.info(f"Forwarding auth request: {path}")
            response = await self.handle_auth_request(request)
            
            # Add CORS headers to auth responses
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        
        response = await call_next(request)
        return response
    
    async def handle_auth_request(self, request: Request):
        path = request.url.path
        query_params = request.query_params._dict
        
        # Log the auth request details
        logging.info(f"Auth request: {path}, params: {query_params}")
        
        # Handle session refresh requests
        if path == "/auth/session/refresh":
            try:
                # Get request body safely
                try:
                    body = await request.json() if request.method == "POST" else {}
                except json.JSONDecodeError:
                    logging.warning("Could not parse request body as JSON")
                    body = {}
                
                logging.info(f"Session refresh request body: {body}")
                
                # Get refresh token from request
                refresh_token = body.get('refreshToken', None)
                logging.info(f"Refresh token: {refresh_token}")
                
                # Generate a front token for SuperTokens
                front_token = f"st-{os.urandom(16).hex()}"
                
                # Return a valid session response with front-token header
                response = JSONResponse(content={
                    "status": "OK",
                    "session": {
                        "handle": f"session-handle-{os.urandom(4).hex()}",
                        "userId": f"user-{os.urandom(4).hex()}",
                        "userDataInJWT": {},
                        "accessTokenPayload": {}
                    }
                })
                
                # Add the front-token header that SuperTokens expects
                response.headers["front-token"] = front_token
                response.headers["Access-Control-Expose-Headers"] = "front-token, anti-csrf"
                
                return response
            except Exception as e:
                logging.error(f"Error in session refresh: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})
        
        # Handle session verification
        if path == "/auth/session/verify":
            # For now, just return a mock session response
            return JSONResponse(content={
                "status": "OK",
                "session": {
                    "handle": "session-handle-123",
                    "userId": "user-123",
                    "userDataInJWT": {}
                }
            })
        
        # Handle Google OAuth flow
        if path == "/auth/oauth/google":
            # Redirect to Google's OAuth page
            google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                "client_id": GOOGLE_CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
                "access_type": "offline",
                "prompt": "consent",
                "include_granted_scopes": "true"
            }
            url = f"{google_auth_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            return RedirectResponse(url=url)
        
        # Handle Google callback
        if path == "/auth/callback/google":
            code = query_params.get("code")
            if not code:
                return JSONResponse(status_code=400, content={"error": "No code provided"})
            
            # Exchange code for tokens
            try:
                token_url = "https://oauth2.googleapis.com/token"
                data = {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
                response = requests.post(token_url, data=data)
                tokens = response.json()
                
                # Get user info
                access_token = tokens.get("access_token")
                if not access_token:
                    return JSONResponse(status_code=400, content={"error": "Failed to get access token"})
                
                userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = requests.get(userinfo_url, headers=headers)
                user_info = userinfo_response.json()
                
                # Create session with SuperTokens
                return RedirectResponse(url="http://localhost:3000/dashboard")
            except Exception as e:
                logging.error(f"Error in Google callback: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})
        
        # Handle /auth/signout
        if path == "/auth/signout":
            return JSONResponse(content={"status": "OK"})
        
        # Add a catch-all route for /auth/thirdparty/* requests
        if path.startswith("/auth/thirdparty/"):
            return JSONResponse(content={"status": "OK"})
        
        # Default response for unhandled auth paths
        logging.warning(f"Unhandled auth path: {path}")
        return JSONResponse(status_code=404, content={"error": f"Auth endpoint not found: {path}"})

# Add SuperTokens middleware
app.add_middleware(SuperTokensMiddleware)

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Mock tenant data (in a real app, this would come from a database)
TENANTS = {
    "tenant1": {
        "id": "tenant1",
        "name": "Demo Tenant",
        "auth_key": "demo-api-key",
    }
}

# Mock user data (in a real app, this would come from a database)
USERS = {
    "user1": {
        "id": "user1",
        "email": "demo@example.com",
        "tenant_id": "tenant1",
    }
}

# Dependency to verify API key and get tenant ID
async def get_tenant_id(api_key: str = Depends(API_KEY_HEADER)):
    """Get tenant ID from API key."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Find tenant by API key
    for tenant_id, tenant in TENANTS.items():
        if tenant["auth_key"] == api_key:
            return tenant_id
    
    raise HTTPException(status_code=401, detail="Invalid API key")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "S4 - Smart S3 Storage Service",
        "version": "0.1.0",
        "status": "online",
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# Auth verification endpoint
@app.get("/api/auth/verify")
async def verify_auth(tenant_id: str = Depends(get_tenant_id)):
    """Verify authentication and return user info."""
    # In a real app, you would look up the user based on session or token
    # For this simple example, we'll just return the first user for the tenant
    for user_id, user in USERS.items():
        if user["tenant_id"] == tenant_id:
            return {
                "authenticated": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "tenant_id": tenant_id,
                }
            }
    
    return {
        "authenticated": False,
        "error": "User not found"
    }

# Files endpoint (mock)
@app.get("/api/files")
async def list_files(tenant_id: str = Depends(get_tenant_id)):
    """List files for the tenant."""
    # In a real app, you would query the database or S3
    return [
        {
            "id": "file1",
            "name": "example.txt",
            "size": 1024,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ]

# Documents endpoint (mock) - Removed duplicate endpoint

# Google auth callback endpoint
@app.get("/auth/callback/google")
async def google_callback(code: str = None, error: str = None, state: str = None, redirect_uri: str = None, request: Request = None):
    """Handle Google OAuth callback."""
    logging.info(f"Received Google OAuth callback with code: {code[:10] if code else 'None'}... and error: {error}")
    logging.info(f"Request headers: {request.headers if request else 'No request object'}")
    
    # Add CORS headers for direct API calls
    headers = {
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-API-Key, fdi-version, st-auth-mode, rid, anti-csrf",
        "Access-Control-Expose-Headers": "Content-Type, Authorization, anti-csrf"
    }
    
    if error:
        logging.error(f"Google OAuth error: {error}")
        return RedirectResponse(
            url="http://localhost:3000/auth/callback/google?error=" + error,
            headers=headers
        )
    
    if not code:
        logging.error("No authorization code provided")
        return RedirectResponse(
            url="http://localhost:3000/auth/callback/google?error=no_code",
            headers=headers
        )
    
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        
        # Important: Use the exact same redirect_uri that was used to get the authorization code
        # Use the provided redirect_uri if available, otherwise use the default
        if not redirect_uri:
            # For direct browser access, use the backend URL
            if request and request.url and str(request.url).startswith("http://localhost:8000"):
                redirect_uri = "http://localhost:8000/auth/callback/google"
            else:
                # Default for requests coming from the frontend
                redirect_uri = REDIRECT_URI
        
        logging.info(f"Using redirect_uri: {redirect_uri}")
        
        # Check if the code has already been used
        if hasattr(google_callback, 'used_codes') and code in google_callback.used_codes:
            logging.error(f"Authorization code has already been used: {code[:10]}...")
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Authorization code has already been used"
                },
                headers=headers
            )
        
        # Store used codes to prevent reuse
        if not hasattr(google_callback, 'used_codes'):
            google_callback.used_codes = set()
        google_callback.used_codes.add(code)
        
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        logging.info(f"Token request data: {token_data}")
        
        logging.info(f"Exchanging code for tokens with redirect_uri: {redirect_uri}")
        
        try:
            token_response = requests.post(token_url, data=token_data)
            logging.info(f"Token response status: {token_response.status_code}")
            
            if not token_response.ok:
                error_details = token_response.text
                try:
                    error_json = token_response.json()
                    logging.error(f"Token exchange error JSON: {error_json}")
                    error_details = json.dumps(error_json)
                except:
                    logging.error(f"Token exchange error text: {error_details}")
                
                return JSONResponse(
                    content={
                        "success": False,
                        "error": f"Token exchange failed: {token_response.status_code}",
                        "details": error_details
                    },
                    headers=headers
                )
        except Exception as e:
            logging.error(f"Exception during token exchange: {str(e)}")
            return JSONResponse(
                content={
                    "success": False,
                    "error": f"Exception during token exchange: {str(e)}"
                },
                headers=headers
            )
            
        token_json = token_response.json()
        logging.info(f"Received tokens: {token_json.keys()}")
        
        # Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        auth_headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        user_response = requests.get(user_info_url, headers=auth_headers)
        
        if not user_response.ok:
            logging.error(f"User info error: {user_response.status_code} - {user_response.text}")
            return JSONResponse(
                content={
                    "success": False,
                    "error": f"Failed to get user info: {user_response.status_code}",
                    "details": user_response.text
                },
                headers=headers
            )
            
        user_info = user_response.json()
        logging.info(f"User info: {user_info.keys()}")
        
        # Create a session token
        session_token = f"st-{user_info['sub']}-{os.urandom(16).hex()}"
        
        # Check if this is an API call or browser request
        accept_header = request.headers.get("accept", "") if request else ""
        is_api_call = "application/json" in accept_header
        
        response_data = {
            "success": True,
            "token": session_token,
            "email": user_info["email"],
            "user": {
                "id": user_info["sub"],
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", "")
            }
        }
        
        # For API calls, return JSON response
        if is_api_call:
            logging.info("Returning JSON response for API call")
            return JSONResponse(content=response_data, headers=headers)
        
        # For browser redirects, redirect to dashboard with token and email
        redirect_url = f"http://localhost:3000/auth/callback/google?token={session_token}&email={user_info['email']}"
        
        logging.info(f"Authentication successful for user: {user_info['email']}")
        logging.info(f"Token generated: {session_token}")
        logging.info(f"Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, headers=headers)
        
    except Exception as e:
        logging.error(f"Error in Google OAuth flow: {str(e)}")
        error_response = {
            "success": False,
            "error": str(e)
        }
        
        # Return JSON for API calls, redirect for browser requests
        accept_header = request.headers.get("accept", "") if request else ""
        if "application/json" in accept_header:
            return JSONResponse(content=error_response, headers=headers)
        else:
            return RedirectResponse(
                url=f"http://localhost:3000/auth/callback/google?error={str(e)}",
                headers=headers
            )



# Document storage configuration
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_docs")

# Create uploads directory if it doesn't exist
os.makedirs(DOCS_DIR, exist_ok=True)
logging.info(f"Local document storage directory: {DOCS_DIR}")

# AWS S3 Configuration - Commented out for now due to permission issues
# S3_BUCKET_NAME = "s4-user-documents"
# S3_REGION = "us-west-2"

# Initialize S3 client - Using local storage instead
s3_client = None
logging.info("Using local storage for document uploads")

# Document upload endpoint
@app.post("/documents/upload")
async def upload_document(request: Request):
    try:
        # Get form data
        form_data = await request.form()
        file = form_data.get("file")
        
        if not file:
            return JSONResponse(status_code=400, content={"error": "No file provided"})
        
        # Get file content and metadata
        content = await file.read()
        filename = file.filename
        file_size = len(content)
        file_type = file.content_type or "application/octet-stream"
        
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # Get user info from request or token
        user_id = "user123"  # Default user ID if not available
        user_email = "user@example.com"  # Default email if not available
        
        # Try to get actual user info from token in header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Extract user ID from token if possible
            if token.startswith("st-"):
                parts = token.split("-")
                if len(parts) > 1:
                    user_id = parts[1]
        
        # Get user email from query params or form data
        user_email = request.query_params.get("email") or form_data.get("email") or user_email
        
        # Create user-specific folder in local storage
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        user_dir = os.path.join(DOCS_DIR, user_folder)
        os.makedirs(user_dir, exist_ok=True)
        
        # Create document-specific folder
        doc_dir = os.path.join(user_dir, doc_id)
        os.makedirs(doc_dir, exist_ok=True)
        
        # Save file to local storage
        file_path = os.path.join(doc_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create URLs for viewing and downloading the file
        file_url = f"/documents/view/{user_folder}/{doc_id}/{filename}"
        download_url = f"/documents/download/{user_folder}/{doc_id}/{filename}"
        
        # Create document metadata file
        metadata = {
            "id": doc_id,
            "name": filename,
            "size": file_size,
            "type": file_type,
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "user_email": user_email,
            "tokens": file_size // 4,  # Rough estimate of tokens
            "url": file_url,
            "download_url": download_url
        }
        
        # Save metadata
        metadata_path = os.path.join(doc_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logging.info(f"Document uploaded successfully: {doc_id}, path: {file_path}")
        
        return JSONResponse(content={
            "success": True,
            "documentId": doc_id,
            "filename": filename,
            "url": file_url,
            "download_url": download_url,
            "message": "Document uploaded successfully"
        })
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Document list endpoint
@app.get("/documents")
async def get_documents(request: Request):
    try:
        # Get user info from request or token
        user_id = "user123"  # Default user ID if not available
        
        # Try to get actual user info from token in header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Extract user ID from token if possible
            if token.startswith("st-"):
                parts = token.split("-")
                if len(parts) > 1:
                    user_id = parts[1]
        
        # Create user-specific folder path
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        user_dir = os.path.join(DOCS_DIR, user_folder)
        
        documents = []
        
        # Check if user directory exists
        if os.path.exists(user_dir) and os.path.isdir(user_dir):
            # List all document directories
            for doc_id in os.listdir(user_dir):
                doc_dir = os.path.join(user_dir, doc_id)
                
                # Skip if not a directory
                if not os.path.isdir(doc_dir):
                    continue
                
                # Check for metadata file
                metadata_path = os.path.join(doc_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        
                        # Add document to the list
                        documents.append(metadata)
                    except Exception as e:
                        logging.error(f"Error reading metadata for document {doc_id}: {str(e)}")
                else:
                    # If no metadata file, try to create one from the files in the directory
                    for filename in os.listdir(doc_dir):
                        if filename != "metadata.json":
                            file_path = os.path.join(doc_dir, filename)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path)
                                file_url = f"/documents/view/{user_folder}/{doc_id}/{filename}"
                                
                                # Create basic metadata
                                documents.append({
                                    "id": doc_id,
                                    "name": filename,
                                    "size": file_size,
                                    "type": "application/octet-stream",
                                    "url": file_url,
                                    "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                                    "user_id": user_id,
                                    "tokens": file_size // 4  # Rough estimate
                                })
        
        logging.info(f"Found {len(documents)} documents for user {user_id}")
        return JSONResponse(content=documents)
    except Exception as e:
        logging.error(f"Error getting documents: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Document delete endpoint
@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, request: Request):
    try:
        # Get user info from request or token
        user_id = "user123"  # Default user ID if not available
        
        # Try to get actual user info from token in header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Extract user ID from token if possible
            if token.startswith("st-"):
                parts = token.split("-")
                if len(parts) > 1:
                    user_id = parts[1]
        
        # Create user-specific folder path
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        user_dir = os.path.join(DOCS_DIR, user_folder)
        doc_dir = os.path.join(user_dir, doc_id)
        
        # Check if document directory exists
        if os.path.exists(doc_dir) and os.path.isdir(doc_dir):
            # Delete all files in the document directory
            for filename in os.listdir(doc_dir):
                file_path = os.path.join(doc_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f"Deleted file: {file_path}")
            
            # Remove the document directory
            os.rmdir(doc_dir)
            logging.info(f"Deleted document directory: {doc_dir}")
        else:
            logging.warning(f"Document directory not found: {doc_dir}")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Document {doc_id} deleted successfully"
        })
    except Exception as e:
        logging.error(f"Error deleting document: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Document view endpoint
@app.get("/documents/view/{user_id}/{doc_id}/{filename}")
async def view_document(user_id: str, doc_id: str, filename: str):
    try:
        # Construct the file path
        file_path = os.path.join(DOCS_DIR, user_id, doc_id, filename)
        
        # Check if file exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return JSONResponse(
                status_code=404,
                content={"error": "Document not found"}
            )
        
        # Determine content type based on file extension
        content_type = "application/octet-stream"  # Default
        if filename.lower().endswith(".pdf"):
            content_type = "application/pdf"
        elif filename.lower().endswith(".txt"):
            content_type = "text/plain"
        elif filename.lower().endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.lower().endswith(".md"):
            content_type = "text/markdown"
        
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Return file content with appropriate headers for viewing
        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logging.error(f"Error viewing document: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Document download endpoint
@app.get("/documents/download/{user_id}/{doc_id}/{filename}")
async def download_document(user_id: str, doc_id: str, filename: str):
    try:
        # Construct the file path
        file_path = os.path.join(DOCS_DIR, user_id, doc_id, filename)
        
        # Check if file exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return JSONResponse(
                status_code=404,
                content={"error": "Document not found"}
            )
        
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Return file content with appropriate headers for download
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logging.error(f"Error downloading document: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Document query endpoint for semantic search
@app.post("/documents/query")
async def query_documents(request: Request):
    try:
        # Get user info from request or token
        user_id = "user123"  # Default user ID if not available
        
        # Try to get actual user info from token in header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Extract user ID from token if possible
            if token.startswith("st-"):
                parts = token.split("-")
                if len(parts) > 1:
                    user_id = parts[1]
        
        # Create user-specific folder path
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        
        # Parse request body
        body = await request.json()
        query = body.get("query")
        document_ids = body.get("document_ids", [])
        
        # Validate query
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Query is required"}
            )
        
        # Log query for debugging
        logging.info(f"Processing document query: {query}")
        logging.info(f"Document IDs filter: {document_ids}")
        
        # In a real implementation, this would use an embedding model and vector search
        # For this demo, we'll return a simulated response
        
        # Get list of user's documents to use as sources
        user_docs_dir = os.path.join(DOCS_DIR, user_folder)
        available_docs = []
        
        if os.path.exists(user_docs_dir):
            # If document_ids is provided, filter to only those documents
            doc_dirs = [d for d in os.listdir(user_docs_dir) 
                       if os.path.isdir(os.path.join(user_docs_dir, d)) and 
                       (not document_ids or d in document_ids)]
            
            for doc_id in doc_dirs:
                doc_dir = os.path.join(user_docs_dir, doc_id)
                metadata_file = os.path.join(doc_dir, "metadata.json")
                
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        available_docs.append({
                            "document_id": doc_id,
                            "document_name": metadata.get("filename", "unknown.pdf"),
                            "relevance_score": round(random.uniform(0.7, 0.95), 2)  # Simulated relevance score
                        })
        
        # Sort by simulated relevance score
        available_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Limit to top 3 most relevant docs
        top_docs = available_docs[:3]
        
        # Generate a simulated answer based on the query
        sample_answers = [
            f"Based on your documents, the answer to '{query}' is that the project timeline has been extended by two weeks due to supply chain issues.",
            f"According to the documents, regarding '{query}', the quarterly revenue exceeded projections by 12% with strongest growth in the enterprise segment.",
            f"The documents indicate that for '{query}', the team should focus on improving the user onboarding experience as it has the highest drop-off rate.",
            f"Your documents suggest that '{query}' relates to the new product launch scheduled for Q3, with initial market testing showing positive results."
        ]
        
        answer = random.choice(sample_answers)
        
        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "answer": answer,
                "sources": top_docs
            }
        )
    except Exception as e:
        logging.error(f"Error processing document query: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Main function to run the server
def main():
    """Run the server."""
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))  # Using port 8000 as requested
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
