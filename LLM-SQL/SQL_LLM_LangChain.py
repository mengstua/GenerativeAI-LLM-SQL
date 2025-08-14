"""
SQL_LLM_LangChain.py

This script demonstrates how to use LangChain and Google Gemini 2.0 Flash to translate natural language questions into SQL queries and execute them on the Chinook SQLite database.
"""

import sqlite3
import pandas as pd

import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

import os
from dotenv import load_dotenv


# 1. Creating the Chinook database
print("1. Creating the Chinook database")

db_path = 'Chinook.db'
chinook_sql_path = 'data/Chinook_Sqlite.sql'  

try:
    with open(chinook_sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
except FileNotFoundError:
    print(f"Error: SQL file not found at {chinook_sql_path}.")
    exit(1)
except Exception as e:
    print(f"Error reading SQL file: {e}")
    exit(1)

try:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
    print('Chinook database schema and data loaded using sqlite3.')
except sqlite3.Error as e:
    print(f"Error creating/loading database: {e}")
    exit(1)

# Check if data is present in the Artist table
try:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Artist')
        print('Number of rows in Artist table:', cursor.fetchone()[0])
except sqlite3.Error as e:
    print(f"Error checking Artist table: {e}")

print(" -> Chinook database created successfully.")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# 2. Connect to the SQLite database and display schema
print("2. Connect to the SQLite database and display schema")

try:
    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
    exit(1)

def display_schema(conn):
    """
    Extract and return a string representation of the database schema.
    Args:
        conn: sqlite3.Connection object
    Returns:
        str: Formatted schema string
    """
    schema = ""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables  = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        for table in tables:
            schema += f"table: {table}\nColumns:\n"
            cursor.execute(f"PRAGMA table_info({table})")
            for column in cursor.fetchall():
                schema += f"  - {column[1]} ({column[2]})\n"
            schema += "\n"
    except Exception as e:
        schema += f"Error extracting schema: {e}\n"
    return schema

schema = display_schema(cursor)
print(schema[:1000])  # Display the first 1000 characters of the schema

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# 3 creating a prompt template for the LLM
print("3. Creating a prompt template for the LLM")


# Load environment variables from .env file
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE-API-KEY")
    if not api_key:
        raise ValueError("GOOGLE-API-KEY not found in .env file.")
    os.environ["GOOGLE_API_KEY"] = api_key
except Exception as e:
    print(f"Error loading API key: {e}")
    exit(1)

prompt = PromptTemplate.from_template(
    """ 
Your are a SQL assistance. Given a database chema and a natural language request,
write the correct SQL query to answer it. Only use the given schema.
Schema:
{schema}
Question: "{question}"

SQL:
"""
)

print(" -> Prompt template created successfully.")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

### 4 Prompting the AI agent
print("4. Prompting the AI agent")


# Use the Gemini 2.0 Flash model for the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
output_parser = StrOutputParser()

print(" -> prompt carried out successfully .")

# Chain: prompt -> LLM -> output parser
chain: Runnable = prompt | llm | output_parser

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# 5 Parsing the LLM SQL Output and Execute it
print("5. Parsing the LLM SQL Output and Execute it")


def process_question(question: str):
    """
    Given a natural language question, generate a SQL query using the LLM and execute it on the database.
    Args:
        question (str): The user's natural language question.
    Returns:
        tuple: (sql_query, result) where result is a DataFrame or error message.
    """
    try:
        sql_query = chain.invoke({"schema": schema, "question": question}).strip()
    except Exception as e:
        return None, f"Error generating SQL with LLM: {e}"
    # Remove markdown code block markers if present
    if sql_query and sql_query.startswith('```sql') and sql_query.endswith('```'):
        sql_query = sql_query[6:-3].strip()
    elif sql_query and sql_query.startswith('```') and sql_query.endswith('```'):
        sql_query = sql_query[3:-3].strip()
    try:
        result = pd.read_sql_query(sql_query, conn)
    except Exception as e:
        result = f"Error executing SQL: {e}"
    return sql_query, result

print(" -> SQL query and result processing function ready.")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# 6 Testing with few questions
print("6. Testing with few questions")

from IPython.display import display
# Set pandas display options for better notebook output
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)

questions = [
    "List all customers in Canada.",
    "Which employees are sales agents?",
    "What are the 5 most purchased tracks?",
    "Show total sales per country in decending order.",
    "Which artists have more than 5 albums?",
    "list three expensive albums",
    "What is the total revenue from sales?",
 ]
for question in questions:
    sql_query, result = process_question(question)
    print(f"\nQuestion: {question}")
    print(f"SQL Query: {sql_query}")
    print("Result:")
    if isinstance(result, pd.DataFrame):
        display(result)  # Show as scrollable table in notebook
    else:
        print(result)
    print("\n" + "="*100 + "\n")

