import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

load_dotenv()  # loads variables from .env in current directory

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432)
        )
        print("Connection successful")
        conn.close()
    except OperationalError as e:
        print(f"Connection failed: {e}")
print("DB:", os.getenv("DB_NAME"))
print("USER:", os.getenv("DB_USER"))
print("PASS:", os.getenv("DB_PASSWORD"))
print("HOST:", os.getenv("DB_HOST"))
print("PORT:", os.getenv("DB_PORT"))
if __name__ == "__main__":
    test_connection()