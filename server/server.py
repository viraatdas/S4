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
import math
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
    allow_origins=[os.environ.get("WEBSITE_DOMAIN", "http://localhost:3000")],  # Frontend URL from environment
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
WEBSITE_DOMAIN = os.environ.get("WEBSITE_DOMAIN", "http://localhost:3000")
REDIRECT_URI = os.environ.get("REDIRECT_URI", f"{WEBSITE_DOMAIN}/auth/callback/google")

# SuperTokens middleware to handle auth requests
class SuperTokensMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Get website domain from environment variable
        website_domain = os.environ.get("WEBSITE_DOMAIN", "http://localhost:3000")
        
        # Handle OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            logging.info(f"Handling OPTIONS request for: {path}")
            headers = {
                "Access-Control-Allow-Origin": website_domain,
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
            response.headers["Access-Control-Allow-Origin"] = website_domain
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
    website_domain = os.environ.get("WEBSITE_DOMAIN", "http://localhost:3000")
    headers = {
        "Access-Control-Allow-Origin": website_domain,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-API-Key, fdi-version, st-auth-mode, rid, anti-csrf",
        "Access-Control-Expose-Headers": "Content-Type, Authorization, anti-csrf"
    }
    
    if error:
        logging.error(f"Google OAuth error: {error}")
        return RedirectResponse(
            url=f"{WEBSITE_DOMAIN}/auth/callback/google?error=" + error,
            headers=headers
        )
    
    if not code:
        logging.error("No authorization code provided")
        return RedirectResponse(
            url=f"{WEBSITE_DOMAIN}/auth/callback/google?error=no_code",
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
                redirect_uri = f"{os.environ.get('API_URL', 'http://localhost:8000')}/auth/callback/google"
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
        redirect_url = f"{WEBSITE_DOMAIN}/auth/callback/google?token={session_token}&email={user_info['email']}"
        
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
                url=f"{WEBSITE_DOMAIN}/auth/callback/google?error={str(e)}",
                headers=headers
            )



# Document storage configuration
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_docs")

# Create uploads directory if it doesn't exist
os.makedirs(DOCS_DIR, exist_ok=True)
logging.info(f"Local document storage directory: {DOCS_DIR}")

S3_BUCKET_NAME = os.getenv("S4_S3_BUCKET", "s4-storage-prod")
S3_REGION = os.getenv("S4_S3_REGION", "us-east-1")

import boto3
s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
logging.info(f"Using S3 storage for document uploads: bucket={S3_BUCKET_NAME}, region={S3_REGION}")

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
        
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        s3_key = f"{user_folder}/{doc_id}/{filename}"
        
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=content,
                ContentType=file_type
            )
            logging.info(f"Uploaded file to S3: {s3_key}")
        except Exception as e:
            logging.error(f"Error uploading to S3: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to upload file: {str(e)}"})
        
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
        
        metadata_json = json.dumps(metadata, indent=2)
        metadata_key = f"{user_folder}/{doc_id}/metadata.json"
        
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=metadata_key,
                Body=metadata_json,
                ContentType="application/json"
            )
        except Exception as e:
            logging.error(f"Error saving metadata to S3: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to save metadata: {str(e)}"})
        
        logging.info(f"Document uploaded successfully: {doc_id}, S3 key: {s3_key}")
        
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
        
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        
        documents = []
        
        try:
            prefix = f"{user_folder}/"
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=prefix,
                Delimiter="/"
            )
            
            for prefix_obj in response.get('CommonPrefixes', []):
                doc_prefix = prefix_obj.get('Prefix', '')
                doc_id = doc_prefix.split('/')[-2] if doc_prefix.endswith('/') else doc_prefix.split('/')[-1]
                
                metadata_key = f"{user_folder}/{doc_id}/metadata.json"
                try:
                    metadata_obj = s3_client.get_object(
                        Bucket=S3_BUCKET_NAME,
                        Key=metadata_key
                    )
                    metadata = json.loads(metadata_obj['Body'].read().decode('utf-8'))
                    
                    # Add document to the list
                    documents.append(metadata)
                except Exception as e:
                    logging.error(f"Error reading metadata for document {doc_id}: {str(e)}")
                    
                    try:
                        doc_response = s3_client.list_objects_v2(
                            Bucket=S3_BUCKET_NAME,
                            Prefix=f"{user_folder}/{doc_id}/"
                        )
                        
                        for obj in doc_response.get('Contents', []):
                            key = obj['Key']
                            filename = key.split('/')[-1]
                            
                            if filename != "metadata.json":
                                file_size = obj['Size']
                                file_url = f"/documents/view/{user_folder}/{doc_id}/{filename}"
                                
                                # Create basic metadata
                                documents.append({
                                    "id": doc_id,
                                    "name": filename,
                                    "size": file_size,
                                    "type": "application/octet-stream",
                                    "url": file_url,
                                    "created_at": obj['LastModified'].isoformat() if hasattr(obj['LastModified'], 'isoformat') else str(obj['LastModified']),
                                    "user_id": user_id,
                                    "tokens": file_size // 4  # Rough estimate
                                })
                    except Exception as inner_e:
                        logging.error(f"Error listing files for document {doc_id}: {str(inner_e)}")
        except Exception as e:
            logging.error(f"Error listing documents in S3: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to list documents: {str(e)}"})
        
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
        
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        prefix = f"{user_folder}/{doc_id}/"
        
        try:
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=prefix
            )
            
            if 'Contents' not in response or len(response['Contents']) == 0:
                logging.warning(f"Document not found in S3: {prefix}")
            else:
                # Delete all files in the document directory
                for obj in response['Contents']:
                    s3_client.delete_object(
                        Bucket=S3_BUCKET_NAME,
                        Key=obj['Key']
                    )
                    logging.info(f"Deleted file from S3: {obj['Key']}")
                
                logging.info(f"Deleted document from S3: {prefix}")
        except Exception as e:
            logging.error(f"Error deleting document from S3: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to delete document: {str(e)}"})
        
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
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        s3_key = f"{user_folder}/{doc_id}/{filename}"
        
        try:
            response = s3_client.get_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key
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
            
            content = response['Body'].read()
            
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
            logging.error(f"Error retrieving document from S3: {str(e)}")
            return JSONResponse(
                status_code=404,
                content={"error": "Document not found"}
            )
    except Exception as e:
        logging.error(f"Error viewing document: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Document download endpoint
@app.get("/documents/download/{user_id}/{doc_id}/{filename}")
async def download_document(user_id: str, doc_id: str, filename: str):
    try:
        user_folder = user_id.replace("@", "-at-").replace(".", "-dot-")
        s3_key = f"{user_folder}/{doc_id}/{filename}"
        
        try:
            response = s3_client.get_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key
            )
            
            content = response['Body'].read()
            
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
            logging.error(f"Error retrieving document from S3: {str(e)}")
            return JSONResponse(
                status_code=404,
                content={"error": "Document not found"}
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
        
        import openai
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        available_docs = []
        
        try:
            prefix = f"{user_folder}/"
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=prefix
            )
            
            for obj in response.get('Contents', []):
                key_parts = obj['Key'].split('/')
                if len(key_parts) >= 2:
                    doc_id = key_parts[1]
                    
                    if any(doc['document_id'] == doc_id for doc in available_docs):
                        continue
                    
                    if not document_ids or doc_id in document_ids:
                        metadata_key = f"{user_folder}/{doc_id}/metadata.json"
                        try:
                            metadata_obj = s3_client.get_object(
                                Bucket=S3_BUCKET_NAME,
                                Key=metadata_key
                            )
                            metadata = json.loads(metadata_obj['Body'].read().decode('utf-8'))
                            
                            file_key = None
                            for content_obj in response.get('Contents', []):
                                if content_obj['Key'].startswith(f"{user_folder}/{doc_id}/") and not content_obj['Key'].endswith("metadata.json"):
                                    file_key = content_obj['Key']
                                    break
                            
                            if file_key:
                                available_docs.append({
                                    "document_id": doc_id,
                                    "document_name": metadata.get("filename", "unknown.pdf"),
                                    "file_key": file_key
                                })
                        except Exception as e:
                            logging.error(f"Error getting metadata for document {doc_id}: {str(e)}")
                            continue
        except Exception as e:
            logging.error(f"Error listing documents in S3: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to list documents: {str(e)}"})
        
        import math
        
        try:
            query_embedding_response = client.embeddings.create(
                model=os.getenv("S4_EMBEDDING_MODEL", "text-embedding-3-small"),
                input=query
            )
            query_embedding = query_embedding_response.data[0].embedding
            
            doc_embeddings = []
            for doc in available_docs:
                try:
                    file_obj = s3_client.get_object(
                        Bucket=S3_BUCKET_NAME,
                        Key=doc["file_key"]
                    )
                    content = file_obj['Body'].read().decode('utf-8', errors='replace')
                    
                    doc_embedding_response = client.embeddings.create(
                        model=os.getenv("S4_EMBEDDING_MODEL", "text-embedding-3-small"),
                        input=content[:8000]  # Limit to first 8000 chars to stay within token limits
                    )
                    doc_embedding = doc_embedding_response.data[0].embedding
                    
                    similarity = cosine_similarity(query_embedding, doc_embedding)
                    
                    doc_embeddings.append({
                        "document_id": doc["document_id"],
                        "document_name": doc["document_name"],
                        "relevance_score": round(similarity, 2),
                        "content": content[:500]  # Include a preview of the content
                    })
                except Exception as e:
                    logging.error(f"Error processing document {doc['document_id']}: {str(e)}")
                    continue
            
            doc_embeddings.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            top_docs = doc_embeddings[:5]
            
            context = "\n\n".join([f"Document: {doc['document_name']}\nContent: {doc['content']}" for doc in top_docs])
            
            response = client.chat.completions.create(
                model=os.getenv("S4_DEFAULT_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided document context."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nPlease answer the question based on the provided context."}
                ]
            )
            
            answer = response.choices[0].message.content
            
            # Return response
            return JSONResponse(
                status_code=200,
                content={
                    "answer": answer,
                    "sources": top_docs
                }
            )
        except Exception as e:
            logging.error(f"Error generating embeddings or searching: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to search documents: {str(e)}"})
    except Exception as e:
        logging.error(f"Error processing document query: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 * magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

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
