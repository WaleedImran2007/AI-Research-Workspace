import os
import json
from groq import Groq
from schemas.reflection import Reflection

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def reflect(user_query, plan, context):
    prompt = f"""
    You are a helpful reviewer. Review the execution context for the user query.
    Determine if the context contains sufficient and accurate information to answer the query.

    Query: {user_query}
    Plan: {plan}
    Context: {context}

    Respond strictly with a JSON object containing:
    - "approved": boolean (true if context is sufficient/valid, false otherwise)
    - "action": string (optional, if approved is false, suggest next steps)
    - "reason": string (short explanation of why it passed or failed)

    Examples:

    1. If planning is wrong:

    {{
        "approved": false,
        "action": "replan",
        "reason": "Wrong tool selected"
    }}

    2. If temporary failure of a tool:

    {{
        "approved": false,
        "action": "retry_tool",
        "reason": "Temporary tool failure"
    }}

    3. If the question is unanswerable:

    {{
        "approved": false,
        "action": "stop",
        "reason": "Question cannot be answered"
    }}
    """

    try:
        response = client.chat.completions.create(
            # Switch to 8b-instant to save daily token quota!
            model="llama-3.1-8b-instant",  
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        return Reflection.model_validate_json(content)

    except Exception as e:
        print(f"Reflection step failed: {e}")
        # Fallback to approved=True so your app doesn't crash if reflection fails
        return Reflection(
            approved=True, 
            action=None,
            reason="Reflection fallback: bypassed due to error.")