# app/__init__.py
import os
import time
from flask import Flask
from dotenv import load_dotenv
from .utils import format_datetime_british, escapejs_filter
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from urllib.parse import quote_plus
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


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

    encoded_password = quote_plus(password)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Configure login manager
    login_manager.login_view = "auth.login"
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
                app.logger.warning(f"[DB] Connection failed (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    app.logger.critical("[DB] DATABASE CONNECTION FAILED after multiple attempts")
                    app.logger.critical(
                        f"Connection attempted: postgresql://{user}:****@{host}:{port}/{database}"
                    )
                    raise RuntimeError("[ERROR] Could not connect to the database.") from e

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # Jinja filters
    app.jinja_env.filters["datetime_british"] = format_datetime_british
    app.jinja_env.filters["escapejs"] = escapejs_filter

    # Register error handlers
    from . import error_handlers
    error_handlers.register_handlers(app)

    # CLI commands
    from app import seeder
    app.cli.add_command(seeder.seed_command)

    # Final startup log
    app.logger.info("[SUCCESS] Todo App has started")

    return app