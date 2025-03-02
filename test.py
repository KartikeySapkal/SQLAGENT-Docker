import json
import os
import time
import functools
import mysql.connector
from dotenv import load_dotenv
from ollama import Client
from my_database.db_connector import get_db_connection

# Load environment variables
load_dotenv()

# Initialize Ollama client with timeout and retry settings
client = Client(host='http://localhost:11434')

# Load and process schema information once at startup
with open("my_database/schema_info.json", "r") as file:
    SCHEMA_INFO = json.load(file)

# Create a more compact schema representation for the prompt
SCHEMA_SUMMARY = {}
for table, details in SCHEMA_INFO.items():
    SCHEMA_SUMMARY[table] = {
        "columns": [col["name"] for col in details["columns"]],
        "primary_key": details.get("primary_key", None),
        "foreign_keys": details.get("foreign_keys", [])
    }

# Build an optimized system prompt for SQL generation
SYSTEM_PROMPT_TEMPLATE = """You are an SQL query generator specialized for MySQL/MariaDB.
ONLY OUTPUT THE RAW SQL QUERY WITHOUT ANY EXPLANATIONS OR MARKDOWN.

Database Schema:
{schema}

Guidelines:
- Use exact table/column names from schema
- Prefer JOIN over subqueries for better performance
- Add LIMIT 100 to SELECT queries unless specified otherwise
- Use prepared statement syntax for any user-provided values
- No comments or explanations in the query
"""

# Optimized system prompt with the processed schema
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(
    schema=json.dumps(SCHEMA_SUMMARY, indent=2)
)


# Cache for generated queries to avoid repeated LLM calls
@functools.lru_cache(maxsize=100)
def generate_sql_query(user_prompt):
    """Generate optimized SQL query using LLM with query caching."""
    start_time = time.time()

    # Format user prompt to encourage direct SQL responses
    formatted_prompt = f"Generate ONLY a MySQL query that will: {user_prompt}"

    # Add examples for few-shot learning if this is a first-time query type
    if "JOIN" in user_prompt.upper() or "join" in user_prompt.lower():
        formatted_prompt += "\n\nExample of good JOIN syntax: SELECT a.name, b.value FROM table_a a JOIN table_b b ON a.id = b.a_id"

    # Request generation from LLM
    try:
        response = client.chat(model='llama3.2', messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt}
        ])

        query = response['message']['content'].strip()

        # Clean up the query (remove markdown code blocks if present)
        if query.startswith("```sql"):
            query = query.replace("```sql", "").replace("```", "").strip()
        elif query.startswith("```"):
            query = query.replace("```", "").strip()

        # Log performance metrics
        generation_time = time.time() - start_time
        print(f"Query generation took {generation_time:.2f} seconds")

        return query

    except Exception as e:
        print(f"LLM query generation error: {e}")
        return None


def execute_query(query, limit_results=100):
    """Execute a MySQL query with timeout protection."""
    if not query:
        return "No valid query to execute"

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    results = []
    try:
        # Set a query timeout to prevent long-running queries
        cursor = conn.cursor(dictionary=True)

        # Add query timeout (for MySQL 8.0+)
        cursor.execute("SET SESSION MAX_EXECUTION_TIME=10000")  # 10 seconds timeout

        # Execute query with timeout safety
        start_time = time.time()
        cursor.execute(query)

        # Handle different query types
        if query.strip().lower().startswith("select"):
            results = cursor.fetchmany(size=limit_results)
            execution_time = time.time() - start_time
            summary = {
                "execution_time": f"{execution_time:.3f} seconds",
                "rows_returned": len(results),
                "query_type": "SELECT"
            }
            return {"summary": summary, "results": results}
        else:
            conn.commit()
            affected_rows = cursor.rowcount
            execution_time = time.time() - start_time
            summary = {
                "execution_time": f"{execution_time:.3f} seconds",
                "affected_rows": affected_rows,
                "query_type": query.strip().split()[0].upper()
            }
            return {"summary": summary}

    except mysql.connector.Error as err:
        return f"Query execution error: {err}"
    finally:
        if conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    # Example usage with improved prompt for better SQL generation
    user_request = "Get all machine names from tbl_machine_master."

    # Generate SQL query with timing
    start = time.time()
    sql_query = generate_sql_query(user_request)
    print(f"\nGenerated SQL Query ({time.time() - start:.2f}s):\n{sql_query}")

    # Execute and display results in a structured format
    result = execute_query(sql_query)

    if isinstance(result, dict):
        print("\nExecution Summary:")
        for key, value in result["summary"].items():
            print(f"  {key}: {value}")

        if "results" in result:
            print("\nResults:")
            for i, row in enumerate(result["results"]):
                print(f"  {i + 1}. {row}")
    else:
        print(result)