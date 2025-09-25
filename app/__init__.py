# In app/__init__.py
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Standard Flask imports
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from urllib.parse import quote_plus
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Import Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import Flask-WTF for CSRF protection
from flask_wtf.csrf import CSRFProtect

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()  # Initialize CSRF protection


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Configure app
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    # DB config
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")

    if not all([user, password, host, port, database]):
        raise RuntimeError("Database environment variables are not fully set.")

    # Fix Pylance warning: ensure password is not None before quote_plus
    encoded_password = quote_plus(password) if password else ""
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection

    # Configure rate limiter using app.config (Flask-Limiter v3+ API)
    app.config['RATELIMIT_DEFAULT'] = "200 per day, 50 per hour"  # Comma-separated string
    app.config['RATELIMIT_STORAGE_URI'] = "memory://"
    app.config['RATELIMIT_STRATEGY'] = "fixed-window"
    app.config['RATELIMIT_HEADERS_ENABLED'] = True

    # Initialize the limiter with the app
    limiter.init_app(app)

    # Configure login manager
    login_manager.login_view = "auth.login"  # type: ignore  # Pylance false positive - this is correct Flask-Login usage
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    #####DO NOT DELETE########################
    # Register blueprints
    from .routes.main import bp as main_bp
    from .routes.admin import admin_bp
    from .routes.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    #####DO NOT DELETE########################

    # Setup logging BEFORE any log statements
    if not app.debug:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/todo_app.log", maxBytes=10_485_760, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Import models and check DB with retry logic
    with app.app_context():
        from . import models

        max_retries = 5
        for attempt in range(max_retries):
            try:
                db.session.execute(text("SELECT 1"))
                app.logger.info("[DB] Database connection successful.")
                break
            except OperationalError as e:
                app.logger.warning(
                    f"[DB] Connection failed (attempt {attempt + 1}/{max_retries})"
                )
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    app.logger.critical(
                        "[DB] DATABASE CONNECTION FAILED after multiple attempts"
                    )
                    app.logger.critical(
                        f"Connection attempted: postgresql://{user}:****@{host}:{port}/{database}"
                    )
                    raise RuntimeError(
                        "[ERROR] Could not connect to the database."
                    ) from e

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # Jinja filters
    from .utils import format_datetime_british, escapejs_filter

    app.jinja_env.filters["datetime_british"] = format_datetime_british
    app.jinja_env.filters["escapejs"] = escapejs_filter

    # ==================== SECURITY MIDDLEWARE ====================

    # Request validation middleware
    @app.before_request
    def validate_request():
        try:
            # Check for extremely malformed requests
            if not request.environ.get("REQUEST_METHOD"):
                app.logger.warning(f"Suspicious request from {request.remote_addr}")
                return "Bad Request", 400

            # Validate headers aren't excessively large (8KB limit)
            header_size = sum(len(str(k)) + len(str(v)) for k, v in request.headers)
            if header_size > 8192:
                app.logger.warning(
                    f"Large headers blocked from {request.remote_addr} (size: {header_size})"
                )
                return "Request Header Fields Too Large", 431

            # Validate content length (10MB limit)
            if request.content_length and request.content_length > 10 * 1024 * 1024:
                app.logger.warning(
                    f"Large request body blocked from {request.remote_addr} (size: {request.content_length})"
                )
                return "Request Entity Too Large", 413

        except Exception as e:
            app.logger.warning(
                f"Request validation error from {request.remote_addr}: {e}"
            )
            return "Bad Request", 400

    # ==================== END SECURITY MIDDLEWARE ====================

    # Register error handlers
    from . import error_handlers

    error_handlers.register_handlers(app)

    # Rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(
            f"Rate limit exceeded for IP: {get_remote_address()} - {e.description}"
        )
        return {
            "error": "Rate limit exceeded",
            "message": str(e.description),
            "retry_after": getattr(e, "retry_after", None),
        }, 429

    # CSRF error handler
    @app.errorhandler(400)
    def csrf_error(reason):
        app.logger.warning(f"CSRF error: {reason}")
        return {
            "error": "CSRF token missing or invalid",
            "message": "Please refresh the page and try again",
        }, 400

    # CLI commands
    from . import seeder

    app.cli.add_command(seeder.seed_command)

    ####################COOKIES#########################
    # Set visitor cookie for anonymous users
    from app.security.rate_limit import set_visitor_cookie_if_needed

    @app.after_request
    def after_request(response):
        # Set visitor cookie if needed
        response = set_visitor_cookie_if_needed(response)
        return response

    ####################COOKIES#########################

    # Final startup log
    app.logger.info("[SUCCESS] Todo App has started")

    # --- Add CSP Header ---
    @app.after_request
    def add_security_headers(response):
        # --- CSP Policy (ensure frame-ancestors is present) ---
        csp_policy = (
            f"default-src 'self'; "
            f"script-src 'self'; " # Adjust as needed
            f"style-src 'self' 'unsafe-inline'; " # Adjust as needed
            f"img-src 'self' ; "
            f"font-src 'self'; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'; " # Modern ClickJacking protection
            f"base-uri 'self'; "
            f"form-action 'self'; "
            # Optional reporting:
            # "report-uri /csp-report;"
            f"object-src 'none'; " # <--- Add this line
        )
        response.headers['Content-Security-Policy'] = csp_policy

        # --- Additional Security Headers ---
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # --- Add X-Frame-Options for older browser compatibility ---
        # Use 'DENY' to match 'frame-ancestors 'none';' or 'SAMEORIGIN' to match 'frame-ancestors 'self';'
        response.headers['X-Frame-Options'] = 'DENY' # <--- Add this line
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # If using HTTPS, set HSTS (often better done by web server/nginx):
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    return app
