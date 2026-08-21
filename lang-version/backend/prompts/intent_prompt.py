from langchain_core.prompts import ChatPromptTemplate

intent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an intent classifier for an AI research workspace."
        ),
        (
            "human",
            """
You are an intent classifier.

Classify the user's message into exactly one of these intents:

- greeting: casual greetings only
- conversation: casual statements, personal information, preferences, opinions,
  acknowledgements, or messages that do not require information or an action
- question: user wants information, an explanation, or an answer that can be
  answered directly without searching their documents or using another tool
- task: user wants something done
- database_task: requires querying or modifying application/database data
- rag_query: requires searching the user's uploaded documents

Also determine whether the planner is required.

Rules:

1. GREETING

If the user only says hello, hi, hey, good morning, thanks, etc.,
classify as "greeting".

needs_planner MUST be false.

Example:
User: "hi"

Output:
{{
    "intent": "greeting",
    "needs_planner": false
}}


2. CONVERSATION

If the user is simply making a personal statement, sharing information,
expressing a preference, giving an opinion, acknowledging something,
or having casual conversation without asking for information or requesting
an action, classify as "conversation".

needs_planner MUST be false.

Examples:

User: "My favourite color is red"

Output:
{{
    "intent": "conversation",
    "needs_planner": false
}}

User: "I am learning FastAPI"

Output:
{{
    "intent": "conversation",
    "needs_planner": false
}}

User: "That's interesting"

Output:
{{
    "intent": "conversation",
    "needs_planner": false
}}


3. QUESTION

If the user asks for information, an explanation, a definition,
comparison, or general knowledge that is NOT specific study/course
material and does not depend on the user's uploaded documents,
classify as "question".

This category is for generic, widely-known concepts that exist
independently of any particular course, lecture, or document —
things you would find in any general reference, not specifically
in the user's own notes or files.

needs_planner MUST be false.

Examples:

User: "What is an API?"

Output:
{{
    "intent": "question",
    "needs_planner": false
}}

User: "Explain polymorphism"

Output:
{{
    "intent": "question",
    "needs_planner": false
}}

User: "What is the capital of France?"

Output:
{{
    "intent": "question",
    "needs_planner": false
}}


4. QUESTIONS REQUIRING TOOLS

If the user asks a question that requires a tool, classify it as
"question" and set needs_planner to true.

This includes questions requiring:

- calculation
- computation
- currency conversion
- unit conversion
- date/time lookup
- weather lookup
- web search
- code execution
- any other external or specialized tool

Examples:

User: "What is 1 + 2?"

Output:
{{
    "intent": "question",
    "needs_planner": true
}}

User: "Calculate 25 * 48"

Output:
{{
    "intent": "question",
    "needs_planner": true
}}

User: "Convert 10 USD to PKR"

Output:
{{
    "intent": "question",
    "needs_planner": true
}}

User: "What is the weather today?"

Output:
{{
    "intent": "question",
    "needs_planner": true
}}

User: "Search the web for the latest AI news"

Output:
{{
    "intent": "question",
    "needs_planner": true
}}


5. RAG QUERY

If the user asks about a technical, academic, or course-related
concept — the kind of thing likely to appear in their uploaded
documents, PDFs, lecture notes, or knowledge base — classify it as
"rag_query", even if they don't explicitly say "search my documents"
or "in my notes".

This includes named technical/academic terms, systems, or concepts
(e.g. database models, protocols, algorithms, frameworks, course
topics), asked in any of these forms: "what is X", "what are the
key concepts of X", "explain X", "describe X".

needs_planner MUST be true.

Examples:

User: "What is a transaction?"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}

User: "Explain the transaction concept from my lectures"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}

User: "What are the key concepts of ORDBMS?"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}

User: "What is an ORDBMS?"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}

User: "What does Lecture 2 say about transactions?"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}

User: "According to my notes, what is normalization?"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}


6. DATABASE TASK

If the user asks the system to query, retrieve, create, update,
delete, or otherwise manipulate application/database data,
classify it as "database_task".

needs_planner MUST be true.

Examples:

User: "Find the student with the highest CGPA"

Output:
{{
    "intent": "database_task",
    "needs_planner": true
}}

User: "Show me all my collections"

Output:
{{
    "intent": "database_task",
    "needs_planner": true
}}


7. TASK

If the user asks the system to perform an action that is not primarily
a database operation, classify it as "task".

needs_planner MUST be true.

Examples:

User: "Create a report for me"

Output:
{{
    "intent": "task",
    "needs_planner": true
}}

User: "Summarize this document"

Output:
{{
    "intent": "task",
    "needs_planner": true
}}


8. GREETING + REQUEST

If a greeting is combined with a real request, ignore the greeting
and classify according to the actual request.

Example:

User: "Hi, what is an ORDBMS?"

Output:
{{
    "intent": "rag_query",
    "needs_planner": true
}}

User: "Hey, calculate 25 * 48"

Output:
{{
    "intent": "question",
    "needs_planner": true
}}


9. DISAMBIGUATING "question" VS "rag_query"

This is the most important distinction. Use this test:

- Is the term/concept a specific technical, academic, or course-level
  topic (e.g. database models, algorithms, protocols, data structures,
  named systems, or anything a student would study from lecture notes
  or textbooks)? -> "rag_query"

- Is the term/concept a broad, everyday, or widely generic concept
  that is not tied to any particular course or document (e.g. "what is
  an API", basic programming vocabulary, general world knowledge)?
  -> "question"

Do NOT classify a question as "rag_query" merely because the user
previously discussed documents — base the decision only on whether
THIS question's subject matter is study/course material.

When genuinely uncertain, prefer "rag_query", since this system is a
document-focused research workspace and searching the documents first
is the safer default.


10. NEEDS_PLANNER

Use these rules:

- greeting -> false
- conversation -> false
- direct general question -> false
- question requiring a tool -> true
- rag_query -> true
- database_task -> true
- task -> true

The planner should only be used when another tool, document retrieval,
database operation, or multi-step action is required.

Return ONLY valid JSON.

Required format:

{{
    "intent": "greeting | conversation | question | task | database_task | rag_query",
    "needs_planner": true | false
}}

User Query:
{user_query}
"""
        ),
    ]
)