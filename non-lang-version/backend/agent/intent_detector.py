from dotenv import load_dotenv
load_dotenv() 

from groq import Groq
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_intent(user_query: str):
    prompt = f"""
You are an intent classifier.

Classify the user's message.

Possible intents:
- greeting: casual greetings only
- question: user wants information/explanation
- task: user wants something done
- database_task: requires database/tools
- rag_query: requires document search

Rules:
- If the user only says hello/hi/thanks, classify as greeting.
- If greeting is combined with a task, classify based on the task.
- Return only JSON.

Examples:

User:
"hi"

Output:
{{
    "intent": "greeting",
    "needs_planner": false
}}

User:
"hi, find the student with highest CGPA"

Output:
{{
    "intent": "database_task",
    "needs_planner": true
}}

User:
"Search my uploaded PDF for authentication"

Output:
{{
    "intent": "rag_query",
    "needs_planner": false
}}

User Query:
{user_query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)