from app import create_app
import sys
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure a simple logger for the startup script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    # The create_app function now handles the initial DB connection check.
    app = create_app()
    logging.info("Flask app created successfully")
except RuntimeError as e:
    # This block will now catch the database connection error from create_app
    logging.critical(f"[ERROR] Failed to create Flask app: {e}")
    logging.critical("\nPlease check your database configuration and ensure it is running:")
    logging.critical("1. PostgreSQL server is running.")
    logging.critical("2. Database credentials in .env file are correct.")
    logging.critical("3. The database specified in .env exists.")
    logging.critical("4. The user has the proper permissions on the database.")
    sys.exit(1)
except Exception as e:
    # Catch any other unexpected errors during app creation
    logging.critical(f"An unexpected error occurred during app creation: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    # Use environment variables for host and port for flexibility, with sensible defaults.

    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    logging.info(f"Starting Flask development server on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)