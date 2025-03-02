import mysql.connector
import os
import json
from db_connector import get_db_connection  # Import database connection function

def extract_schema():
    """Extracts database schema (table names and column names) dynamically and saves it as a dictionary."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed"}

    schema_info = {}

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            schema_info[table_name] = [col[0] for col in columns]  # Extract column names

        cursor.close()
        conn.close()

        # Save schema to a JSON file
        with open("schema_info.json", "w") as json_file:
            json.dump(schema_info, json_file, indent=4)

        return schema_info  # Returns a dictionary
    except mysql.connector.Error as err:
        return {"error": str(err)}

# Example usage
if __name__ == "__main__":
    schema = extract_schema()
    print(json.dumps(schema, indent=4))  # Print dictionary format