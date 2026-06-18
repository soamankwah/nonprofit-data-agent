"""
agent.py
Core Claude API integration. Handles two tasks:
1. Explaining data quality issues in plain English
2. Answering natural language questions about program data
"""

import anthropic
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "nonprofit.db"

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a helpful data assistant for nonprofit program staff.
Your job is to explain data findings clearly and suggest practical next steps.

Rules:
- Use plain English. No SQL jargon, no technical terms without explanation.
- Be specific. Name the actual client IDs or records with issues.
- Be encouraging. Staff are doing their best with limited resources.
- Keep responses concise — staff are busy.
- When suggesting actions, make them concrete and doable today.
- Format your response with clear sections and bullet points."""


def get_schema():
    """Returns a plain-English description of the database tables."""
    return """
    Database has two tables:
    
    CLIENTS table: client_id, first_name, last_name, enrollment_date, status 
    (Active/Inactive/Completed/Pending), case_worker, last_updated, program
    
    APPOINTMENTS table: appointment_id, client_id, appointment_date, status 
    (Attended/No-Show/Scheduled), case_worker, notes
    """


def run_query(sql: str) -> list[dict]:
    """Runs a SQL query and returns results as a list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        rows = [{"error": str(e)}]
    finally:
        conn.close()
    return rows


def explain_issues(issues: list[dict]) -> str:
    """
    Takes a list of data quality issues and asks Claude to explain them
    in plain English with actionable recommendations.
    """
    if not issues:
        return "✅ No data quality issues found. Your data looks clean!"

    issues_text = "\n".join([
        f"- {issue['type']}: {issue['description']}" for issue in issues
    ])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
I ran automated checks on our program database and found these issues:

{issues_text}

Please write a clear data quality report for our program manager.
For each issue, explain:
1. What the problem is (in plain English)
2. Why it matters for our program
3. One specific action they can take today to fix it

End with an overall data health score (X out of 10).
"""
        }]
    )
    return response.content[0].text


def answer_question(user_question: str, conversation_history: list = None) -> str:
    """
    Takes a natural language question from staff, converts it to SQL,
    runs the query, and returns a plain-English explanation of the results.
    """
    if conversation_history is None:
        conversation_history = []

    schema = get_schema()

    # Step 1: Ask Claude to generate SQL
    sql_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system="""You are a SQL expert. Given a database schema and a user question, 
        write a single SQLite SQL query to answer it. 
        Return ONLY the SQL query, nothing else. No explanation, no markdown, no backticks.""",
        messages=[{
            "role": "user",
            "content": f"Schema: {schema}\n\nQuestion: {user_question}\n\nSQL query:"
        }]
    )

    sql_query = sql_response.content[0].text.strip()

    # Step 2: Run the query
    results = run_query(sql_query)

    # Step 3: Ask Claude to explain the results
    messages = conversation_history + [{
        "role": "user",
        "content": f"""
The staff member asked: "{user_question}"

I ran this query: {sql_query}

Results: {results}

Please explain what this means in plain English.
If results are empty, say so clearly and suggest why that might be.
If there are concerning patterns, flag them.
Keep your response under 200 words.
"""
    }]

    final_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages
    )

    return final_response.content[0].text


if __name__ == "__main__":
    # Quick test
    print(answer_question("Which clients have missed more than one appointment?"))
