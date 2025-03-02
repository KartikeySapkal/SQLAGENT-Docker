import json
from db_connector import get_db_connection
get_db_connection()
from ollama import Client
client = Client(host='http://localhost:11434')

with open("schema_info.json", "r") as file:
    SCHEMA_INFO = json.load(file)

prompt = f'''
    Based on the following schema information, generate a brief information about Tables.
    {SCHEMA_INFO}
    Generated information should be useful for the user to understand the database.
'''

stream = client.chat(model='deepseek-r1:1.5b', messages=[
    {
    'role': 'user',
    'content':  prompt,
        },
    ],
    options={
        "temperature": 1,
    },
    stream = True,
)

for chunks in stream:
    print(chunks['message']['content'], end="")
