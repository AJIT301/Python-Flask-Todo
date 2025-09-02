# app/error_handlers.py
from flask import render_template, Response, current_app, request
from . import db
import logging

def not_found(error):
    current_app.logger.warning(f"404 Error: {request.url}")
    return render_template("errors/404.html"), 404

def forbidden(error):
    return render_template("errors/403.html"), 403

def too_many_requests(error):
    return render_template("errors/429.html"), 429

def bad_request(error):
    """Handle 400 Bad Request errors"""
    current_app.logger.warning(f"Bad request: {request.url} - {str(error)}")
    return render_template("errors/400.html", error=error), 400

def request_timeout(error):
    """Handle request timeouts"""
    current_app.logger.warning(f"Request timeout: {request.url}")
    return render_template("errors/408.html"), 408

def request_header_fields_too_large(error):
    """Handle 431 Request Header Fields Too Large"""
    current_app.logger.warning(f"Header too large from {request.remote_addr}")
    return render_template("errors/431.html"), 431

def internal_error(error):
    try:
        db.session.rollback()
    except Exception as e:
        current_app.logger.warning(f"DB rollback failed: {str(e)}")

    current_app.logger.error(f"500 Error: {str(error)}", exc_info=True)

    try:
        return render_template("errors/500.html"), 500
    except Exception:
        return Response("Internal Server Error", status=500)

def handle_client_disconnect(error):
    """Handle client disconnects gracefully"""
    current_app.logger.info(f"Client disconnected: {request.remote_addr}")
    return "", 204  # No content

def register_handlers(app):
    app.register_error_handler(400, bad_request)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(408, request_timeout)
    app.register_error_handler(429, too_many_requests)
    app.register_error_handler(431, request_header_fields_too_large)
    app.register_error_handler(500, internal_error)
    # Handle specific client disconnect scenarios
    app.register_error_handler(ConnectionResetError, handle_client_disconnect)
    app.register_error_handler(BrokenPipeError, handle_client_disconnect)