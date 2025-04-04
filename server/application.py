#!/usr/bin/env python3
"""
Application entry point for Elastic Beanstalk deployment.
This file imports the FastAPI app from server.py and exposes it for WSGI servers.
"""

import os
import sys

# Add the parent directory to the path so we can import the server module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app from server.py
from server.server import app as application

# This is required for AWS Elastic Beanstalk
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(application, host="0.0.0.0", port=port)
