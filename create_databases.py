def create_database():
    try:
        import os, sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from shared.config import Mysql_pass
        import mysql.connector as sql

        # -------------------------
        # Database Configuration
        # -------------------------
        DB_CONFIG = {
            "host": "127.0.0.1",
            "user": "root",
            "password": Mysql_pass,
            }

        conn = sql.connect(**DB_CONFIG)
        cur = conn.cursor()

        import os

        schema_path = os.path.abspath("sample_data")+"\\school_database_schema.sql"

        with open(schema_path) as f:
            data = f.read()

        statements = [stmt.strip() for stmt in data.split(";") if stmt.strip()]
        for statement in statements:
            cur.execute(statement)

    except Exception as e:
        conn.rollback()
        print(f'ERROR:{e}')
    finally:
        conn.commit()
        conn.close()
