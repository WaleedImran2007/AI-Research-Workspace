from langchain_core.prompts import ChatPromptTemplate

reflector_prompt = ChatPromptTemplate.from_messages(
[
    (
        "system",
        'You are a helpful assistant that reviews the execution context for user queries.'
    ),

    (
        "human",
        """
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
    )

])