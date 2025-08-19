import os
from flask import Flask
from dotenv import load_dotenv
from .utils import format_datetime_british
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

load_dotenv()  # Load variables from .env file

db = SQLAlchemy()  # This is your main db instance

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Use environment variables, fallback to safe defaults if needed
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    ####################################################
    # Load DB config from environment variables only
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    #####################################################

    if not all([user, password, host, port, database]):
        raise RuntimeError("Database environment variables are not fully set.")

    # URL-encode the password to handle special characters
    encoded_password = quote_plus(password)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    print(f"DB URI: postgresql://{user}:***@{host}:{port}/{database}")
    
    # Initialize db with app
    db.init_app(app)

    # Import models AFTER db is initialized (using relative import)
    from . import models  # Changed to relative import

    # Register Jinja filter
    app.jinja_env.filters["datetime_british"] = format_datetime_british

    # Register Blueprints
    from . import routes
    app.register_blueprint(routes.bp)

    # Register Error Handlers
    from . import error_handlers
    error_handlers.register_handlers(app)
    
    #REGISTER SEEDER COMMAND
    # Register CLI commands
    from app import seeder
    app.cli.add_command(seeder.seed_command)
    
    return app