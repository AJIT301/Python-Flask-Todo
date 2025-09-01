# create_deadlines_table.py
from app import create_app, db
from sqlalchemy import text


def create_deadlines_table():
    app = create_app()

    with app.app_context():
        # Check if table exists
        try:
            result = db.session.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'deadlines'
                );
            """
                )
            ).fetchone()

            if not result[0]:
                print("Creating deadlines table...")
                create_sql = """
                CREATE TABLE deadlines (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    description TEXT,
                    deadline_date TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by_id INTEGER REFERENCES users(id)
                );
                """
                db.session.execute(text(create_sql))
                db.session.commit()
                print("✅ Deadlines table created successfully!")
            else:
                print("✅ Deadlines table already exists!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    create_deadlines_table()
