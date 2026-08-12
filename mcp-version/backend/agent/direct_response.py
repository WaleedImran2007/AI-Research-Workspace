from core.llm import instant_llm

from langchain_core.prompts import ChatPromptTemplate

direct_response_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful, friendly AI assistant. "
        "Engage in a natural, brief, and conversational response to the user's message. "
        "If they shared personal preferences or casual statements, acknowledge them warmly."
    ),
    (
        "human",
        """
            User query:
            {user_query}

            Relevant User Memories:
            {memories}
        """
    ),
])

direct_response_chain = direct_response_prompt | instant_llm