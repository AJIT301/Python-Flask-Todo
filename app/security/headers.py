# app/security/headers.py
"""
Development Security Headers Middleware
"""
import logging
from flask import request

logger = logging.getLogger("SecurityHeaders")

def add_security_headers(response):
    """
    Add development security headers to all responses
    """
    # === XSS Protection ===
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # === Content Type Sniffing Protection ===
    response.headers["X-Content-Type-Options"] = "nosniff"

    # === Clickjacking Protection ===
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # === Content Security Policy (more permissive for development) ===
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'self';"
    )
    response.headers["Content-Security-Policy"] = csp_policy

    # === Referrer Policy ===
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # === Permissions Policy ===
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "fullscreen=(self), "
        "payment=()"
    )

    # === Reduce fingerprinting (development) ===
    response.headers["Server"] = "Server"  # Generic instead of Werkzeug details
    response.headers.pop('X-Powered-By', None)
    
    return response

def security_middleware(app):
    """
    Apply development security middleware to Flask app
    """
    @app.after_request
    def after_request(response):
        response = add_security_headers(response)
        return response
    
    logger.info("Development security headers middleware initialized")