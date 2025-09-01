# app/error_handlers.py
from flask import render_template, Response, current_app, request
from . import db

def not_found(error):
    current_app.logger.warning(f"404 Error: {request.url}")
    return render_template("404.html"), 404

def internal_error(error):
    try:
        db.session.rollback()
    except Exception as e:
        current_app.logger.warning(f"DB rollback failed: {str(e)}")

    current_app.logger.error(f"500 Error: {str(error)}", exc_info=True)

    try:
        return render_template("500.html"), 500
    except Exception:
        return Response("Internal Server Error", status=500)

def forbidden(error):
    return render_template("403.html"), 403

def too_many_requests(error):
    return render_template("429.html"), 429

def register_handlers(app):
    app.register_error_handler(404, not_found)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(429, too_many_requests)
    app.register_error_handler(500, internal_error)