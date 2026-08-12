from langchain_core.prompts import ChatPromptTemplate

intent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an intent classifier."
        ),
        (
            "human",
            """
            You are an intent classifier.

            Classify the user's message into exactly one of these intents:

            - greeting: casual greetings only
            - conversation: casual statements, personal information, preferences, opinions, acknowledgements, or messages that do not require information or an action
            - question: user wants information, an explanation, or an answer
            - task: user wants something done
            - database_task: requires querying or modifying application/database data
            - rag_query: requires searching the user's uploaded documents

            Rules:

            1. If the user only says hello, hi, hey, thanks, etc., classify as "greeting".
            2. If the user provides a personal statement, preference, opinion, or casual statement
               without asking a question or requesting an action, classify as "conversation".
            3. If the user asks for information or an explanation, classify as "question".
            4. If the user asks the system to perform an action, classify as "task".
            5. If the task requires application/database data, classify as "database_task".
            6. If the user asks about information that should be found in their uploaded documents,
               classify as "rag_query".
            7. If a greeting is combined with a request, classify based on the request.

            Examples:

            User:
            "hi"

            Output:
            {{
                "intent": "greeting",
                "needs_planner": false
            }}

            User:
            "My favourite color is red"

            Output:
            {{
                "intent": "conversation",
                "needs_planner": false
            }}

            User:
            "What is a transaction?"

            Output:
            {{
                "intent": "question",
                "needs_planner": true
            }}
            
            User:
            "Create a report for me"

            Output:
            {{
                "intent": "task",
                "needs_planner": true
            }}

            User:
            "Find the student with the highest CGPA"

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
                "needs_planner": true
            }}

            User Query:
            {user_query}
            """
        ),
    ]
)