from app import create_app, db, models
from sqlalchemy import text
import sys

try:
    app = create_app()
    print("✅ Flask app created successfully")
except Exception as e:
    print(f"❌ Failed to create Flask app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        with app.app_context():
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                print("✅ Database connection successful")

            # db.create_all()  # Now models are registered, tables will be created
            # print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL server is running")
        print("2. Database credentials in .env file are correct")
        print("3. Database exists")
        print("4. User has proper permissions")
        sys.exit(1)

    print("🚀 Starting Flask development server...")
    print("🚀 Starting Flask development server...")
    print("🚀 Starting Flask development server...")
    app.run(debug=True)
