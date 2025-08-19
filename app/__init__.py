import os
from flask import Flask
from dotenv import load_dotenv
from .utils import format_datetime_british
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager  # <-- add this
from urllib.parse import quote_plus
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()  # <-- add this

# Import models AFTER db is initialized
from . import models


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

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
    print(f"DB URI: postgresql://{user}:***@{host}:{port}/{database}")
    db.init_app(app)

    # 🔑 Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "routes.login"  # adjust blueprint/endpoint if needed

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # Register Jinja filter
    app.jinja_env.filters["datetime_british"] = format_datetime_british

    # Blueprints
    from . import routes

    app.register_blueprint(routes.bp)

    from . import error_handlers

    error_handlers.register_handlers(app)

    from app import seeder

    app.cli.add_command(seeder.seed_command)

    return app
