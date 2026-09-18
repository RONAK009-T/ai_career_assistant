import pymysql
import os
from config.settings import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
from database.db import get_ssl_kwargs

def create_mysql_database():
    """Connects to MySQL server, creates database if needed, and applies all schema tables automatically."""
    print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        ssl_kwargs = get_ssl_kwargs()
        conn = None

        # First attempt: Connect directly to the specified database (standard for cloud MySQL like Aiven)
        try:
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                autocommit=True,
                **ssl_kwargs
            )
        except Exception:
            # Second attempt: Connect without database and create it (standard for local MySQL root)
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
                autocommit=True,
                **ssl_kwargs
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{DB_NAME}`;")

        cursor = conn.cursor()
        print(f"Database '{DB_NAME}' connected successfully.")

        # Read schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()

            statements = [s.strip() for s in sql_script.split(";") if s.strip()]
            for stmt in statements:
                if stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("USE "):
                    continue
                cursor.execute(stmt)
            print(f"All tables verified/created successfully in '{DB_NAME}'!")

        conn.close()
        return True
    except Exception as e:
        print(f"Error initializing MySQL database: {e}")
        return False

if __name__ == "__main__":
    create_mysql_database()
