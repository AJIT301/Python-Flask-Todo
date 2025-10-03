# app/utils/rate_limit_utils.py
import hashlib
import uuid
from flask import request, g
from flask_login import current_user


def get_smart_visitor_id():
    """
    Smart visitor identification - user-based when logged in,
    cookie-based when anonymous, IP-based as fallback
    """
    # Best: Authenticated user
    if current_user.is_authenticated:
        return f"user:{current_user.id}"

    # Good: Cookie-based visitor
    visitor_id = request.cookies.get("visitor_id")
    if visitor_id:
        return f"visitor:{visitor_id}"

    # Fallback: IP-based
    return f"ip:{request.remote_addr}"


def get_visitor_fingerprint():
    """
    Create a more sophisticated fingerprint for anonymous users
    Combines IP, User-Agent, and other browser characteristics
    """
    components = [
        request.remote_addr,  # IP address
        request.headers.get("User-Agent", ""),  # Browser info
        request.headers.get("Accept-Language", ""),  # Language preferences
        request.headers.get("Accept-Encoding", ""),  # Supported encodings
    ]
    fingerprint = "|".join(components)
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def generate_visitor_id():
    """
    Generate a new visitor ID - either from fingerprint or random
    """
    # Try to create deterministic ID from browser fingerprint
    fingerprint = get_visitor_fingerprint()

    # Use first 32 chars of fingerprint + random component for uniqueness
    random_part = str(uuid.uuid4())[:8]
    return f"{fingerprint[:32]}{random_part}"


def set_visitor_cookie_if_needed(response):
    """
    Set visitor cookie if it doesn't exist
    """
    # Only set cookie for anonymous users
    if not current_user.is_authenticated and not request.cookies.get("visitor_id"):
        visitor_id = generate_visitor_id()
        response.set_cookie(
            "visitor_id",
            visitor_id,
            max_age=60 * 60 * 24 * 30,  # 30 days
            httponly=True,  # Prevent XSS access
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",  # CSRF protection
        )
    return response
