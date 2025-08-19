from app import create_app, db
from sqlalchemy import text
from livereload import Server
import sys

try:
    app = create_app()
    print("Flask app created successfully ✅")
except Exception as e:
    print(f"Failed to create Flask app: {e} ❌")
    sys.exit(1)

if __name__ == "__main__":
    try:
        with app.app_context():
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                print("Database connection successful")
    except Exception as e:
        print(f"Database setup failed: {e}")
        sys.exit(1)

    # Flask-LiveReload setup
    server = Server(app.wsgi_app)
    # Watch templates and static files
    server.watch("app/templates/")
    server.watch("app/static/")
    print("Starting Flask development server with LiveReload...")
    server.serve(port=5000, debug=True)