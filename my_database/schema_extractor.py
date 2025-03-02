import json
from db_connector import get_db_connection

def get_schema():
    return extract_schema()


def extract_schema():
    """Extract database schema information and return as JSON."""
    conn = get_db_connection()
    if not conn:
        return json.dumps({"error": "Database connection failed"})

    try:
        cursor = conn.cursor()

        # Get tables
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]

        schema = {}

        # Get column details for each table
        for table in tables:
            cursor.execute(f"DESCRIBE {table};")
            columns = cursor.fetchall()
            schema[table] = [
                {
                    "Field": col[0],
                    "Type": col[1],
                    "Null": col[2],
                    "Key": col[3],
                    "Default": col[4],
                    "Extra": col[5]
                }
                for col in columns
            ]

        cursor.close()
        conn.close()

        return json.dumps(schema, indent=4)
    except Exception as e:
        return json.dumps({"error": str(e)})

