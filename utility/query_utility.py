from my_database.context_generator import SCHEMA_INFO
import json
from ollama import Client
from my_database.db_connector import get_db_connection
import mysql.connector

client = Client(host='http://ollama:11434')

def generate_sql_query(user_prompt):
    """Generate a MySQL query using LLM with schema awareness."""
    system_prompt = f"""
    You are an expert SQL assistant. The user will ask questions about a MySQL database.
    Use the following schema information. Only send the SQL query.:

    {json.dumps(SCHEMA_INFO, indent=4)}

    Rules:
    - Use only table and column names from the schema.
    - Ensure correct SQL syntax and Mariadb syntax.
    - Respond with only the SQL query, nothing else.
    - Do not include any comments in the SQL query.
    """

    response = client.chat(model='llama3.2', messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
                           options={
                               "max_tokens": 200,
                               "temperature": 0.1,
                           }
                           )

    return response['message']['content'].strip()



def execute_query(query):
    """Execute a MySQL query and return results."""
    results = []
    error = None

    conn = get_db_connection()
    if not conn:
        return None, "Failed to connect to database."

    try:
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        cursor.execute(query)

        # Fetch results (if SELECT query)
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
        else:
            conn.commit()
            results = [{"message": "Query executed successfully."}]

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        error = f"Query execution error: {err}"

    return results, error

