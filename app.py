import json
import mysql.connector
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from ollama import Client
from my_database.db_connector import get_db_connection

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Ollama client
client = Client(host='http://ollama:11434')
# client = Client(host='http://localhost:11434')

# Load schema JSON file
with open("my_database/schema_info.json", "r") as file:
    SCHEMA_INFO = json.load(file)


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    user_request = request.form.get('prompt', '')

    try:
        sql_query = generate_sql_query(user_request)
        return jsonify({"status": "success", "query": sql_query})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/execute', methods=['POST'])
def execute():
    query = request.form.get('query', '')

    if not query:
        return jsonify({"status": "error", "message": "No query provided"})

    results, error = execute_query(query)

    if error:
        return jsonify({"status": "error", "message": error})

    return jsonify({"status": "success", "results": results})


if __name__ == "__main__":
    app.run(debug=True, port= 5000)