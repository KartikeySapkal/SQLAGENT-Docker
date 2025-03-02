import mysql.connector
from db_connector import get_db_connection  # Import database connection function

def execute_query(query):
    """Execute a given SQL query and print results."""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute(query)

        # Fetch results if it's a SELECT query
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            for row in results:
                print(row)
        else:
            conn.commit()  # Commit for INSERT, UPDATE, DELETE
            print("Query executed successfully.")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Query execution error: {err}")

# Example usage
if __name__ == "__main__":
    sql_query = ""
    execute_query(sql_query)