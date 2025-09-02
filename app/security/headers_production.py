# app/security/headers_production.py
"""
Production Security Headers Middleware
"""
import logging
from flask import request

logger = logging.getLogger("SecurityHeaders")

def add_production_security_headers(response):
    """
    Add production security headers to all responses
    """
    # === XSS Protection ===
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # === Content Type Sniffing Protection ===
    response.headers["X-Content-Type-Options"] = "nosniff"

    # === Clickjacking Protection ===
    response.headers["X-Frame-Options"] = "DENY"  # More restrictive

    # === HTTPS Enforcement ===
    if request.is_secure or request.headers.get("X-Forwarded-Proto") == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    # === Enhanced Content Security Policy (restrictive) ===
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self'; "  # No unsafe-inline or unsafe-eval
        "style-src 'self'; "    # No unsafe-inline
        "img-src 'self' https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none';"  # More restrictive
    )
    response.headers["Content-Security-Policy"] = csp_policy

    # === Referrer Policy ===
    response.headers["Referrer-Policy"] = "no-referrer"

    # === Enhanced Permissions Policy ===
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "fullscreen=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "gyroscope=(), "
        "speaker=(), "
        "vibrate=(), "
        "accelerometer=()"
    )

    # Override Server header - set it to generic value
    response.headers["Server"] = "Server"
    response.headers.pop('X-Powered-By', None)
    
    return response

def production_security_middleware(app):
    """
    Apply production security middleware to Flask app
    """
    @app.after_request
    def after_request(response):
        response = add_production_security_headers(response)
        return response
    
    logger.info("Production security headers middleware initialized")