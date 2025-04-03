"""
CORS Configuration Module for Piano Chorus Creator Backend

This module provides CORS configuration for the frontend integration.
"""

from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """
    Configure CORS for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Frontend URL
    frontend_url = "https://piano-chorus-creator.lovable.app"
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            frontend_url,
            "http://localhost:3000",  # For local development
            "*"  # Allow all origins temporarily for testing
        ],
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    return app
