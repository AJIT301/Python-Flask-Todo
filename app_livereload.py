from app import create_app, db
from sqlalchemy import text
from livereload import Server
import sys
import logging

# Configure a simple logger for the startup script
logging.basicConfig(
    level=logging.INFO, format="%(asctimes)s - %(levelname)s - %(message)s"
)

try:
    app = create_app()
    logging.info("Flask app created successfully")
except RuntimeError as e:
    logging.critical(f"[ERROR]Failed to create Flask app: {e}")
    logging.critical("\nPlease check your database configuration and ensure it is running.")
    sys.exit(1)
except Exception as e:
    logging.critical(f"An unexpected error occurred during app creation: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    # Flask-LiveReload setup
    server = Server(app.wsgi_app)
    # Watch templates and static files
    server.watch("app/templates/")
    server.watch("app/static/")
    logging.info("Starting Flask development server with LiveReload...")
    server.serve(port=5000, debug=True)