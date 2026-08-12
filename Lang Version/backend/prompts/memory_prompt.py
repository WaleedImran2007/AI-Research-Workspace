from langchain_core.prompts import ChatPromptTemplate

memory_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are a memory detection system.

            Analyze the user's message and determine whether it contains
            information that should be stored as long-term memory.

            Store information that is:
            - A personal preference
            - A lasting interest
            - A useful personal fact
            - A long-term goal
            - A stable user-specific choice

            Do NOT store:
            - Temporary requests
            - Questions
            - General facts
            - One-time instructions
            - Normal conversation that is not useful later

            If the information should be remembered, extract:
            - type
            - key
            - value
            - importance

            If it should not be remembered, set should_store to false.
        """
    ),
    (
        "human",
        """
            User query:
            {user_query}
        """
    )
])