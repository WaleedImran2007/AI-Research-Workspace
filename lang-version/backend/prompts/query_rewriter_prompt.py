from langchain_core.prompts import ChatPromptTemplate

query_rewriter_prompt = ChatPromptTemplate.from_messages(
[
    (
        "system",
        "You are a query rewriting assistant."
    ),

    (
        "human",
        """
        You are a query rewriting assistant.

        Your ONLY job is to resolve references in the user's latest message using
        conversation history, so it can stand alone without needing prior context.

        References to resolve:
        - it, that, this, previous one, above, them, those, etc.

        STRICT RULES:
        - Do NOT answer the question or task.
        - Do NOT change the type of the message. A command stays a command.
        A statement stays a statement. A question stays a question.
        Example: "Multiply two matrices" must stay an instruction like
        "Multiply two matrices" (with any referenced matrices substituted in) —
        it must NOT become "What does it mean to multiply two matrices?"
        - Do NOT add explanation, elaboration, or extra context that isn't in
        the original message.
        - Do NOT rephrase, reword, or "improve" the message otherwise. Change
        the minimum necessary to resolve references.
        - If the message has no references to resolve (no pronouns pointing at
        prior turns), return it completely unchanged, verbatim.

        Conversation History:
        {history}

        Current Message:
        {query}

        Rewritten Message (same type, references resolved, otherwise unchanged):
    """
    )

])