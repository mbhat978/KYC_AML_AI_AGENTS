"""
CORS Configuration
"""


def get_cors_config():
    """Get CORS configuration for the application"""
    return {
        "origins": [
            "http://localhost:5173",      # Vite default
            "http://localhost:3000",      # Alternative React port
            "http://127.0.0.1:5173",      # Localhost IP
            "http://127.0.0.1:3000",
        ],
        "allow_credentials": True,
        "allow_methods": ["*"],           # Allow all HTTP methods
        "allow_headers": ["*"],           # Allow all headers
    }