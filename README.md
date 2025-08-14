# GenAI SQL LLM Project

This AI augmentation project demonstrates how to use Large Language Models (LLMs) with LangChain and Google Gemini 2.0 Flash to translate natural language questions into SQL queries and execute them on the classic Chinook SQLite database.

## Project Structure

- `LLM-SQL/SQL-LLM.ipynb`: Main notebook for natural language to SQL workflow showing step-by-step production.
- `LLM-SQL/data/Chinook_Sqlite.sql`: SQL script to create and populate the Chinook database.
- `LLM-SQL/SQL-LLM-LangChain.py`: The mai Python code of the project.

## Setup Instructions

1. **Clone the repository and open in VS Code.**
2. **Install dependencies:**
   - Python 3.12
   - `pip install -r requirements.txt` 
   - Jupyter or VS Code Jupyter extension
3. **API Key:**
   - Obtain a Google Generative AI API key.
   - Create a `.env` file in the project root
    
4. **Database:**
   - The notebook is automatically create `Chinook.db` from `Chinook_Sqlite.sql`.

## How It Works

- The notebook loads the Chinook database schema and data.
- It displays the schema for LLM context.
- A LangChain prompt template is used to instruct the LLM to generate SQL from natural language.
- The Gemini 2.0 Flash model is used via LangChain.
- The generated SQL is executed on the SQLite database and results are displayed.

## Example Usage

1. Open `practice/SQL-LLM.ipynb` in VS Code or Jupyter.
2. Run all cells. The last cell will:
   - Ask several example questions (e.g., "Which employees are sales agents?")
   - Show the generated SQL and the query results.

## Requirements

Typical requirements (add to `requirements.txt` if needed):
```
pandas
langchain
google-generativeai
langchain-google-genai
python-dotenv
jupyter
```

## Credits

- Chinook Database: https://github.com/lerocha/chinook-database
- LangChain: https://python.langchain.com/
- Google Generative AI: https://ai.google.dev/
