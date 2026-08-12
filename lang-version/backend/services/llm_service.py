import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query: str, context: str, history: str) -> str:
    prompt = f"""
        You are an AI Assistant that provides helpful and accurate answers based on the given context.

        Rules:
        - Answer using only the context. Do not use outside knowledge and do not invent facts or numbers.
        - If the context does not contain the answer, reply exactly: "I could not find the answer to your question in the provided context."
        - If the context only partially answers the question, answer what you can and state what's missing.
        - Use the conversation history only to resolve references (e.g. "it", "that", "the previous one") to figure out what the user is actually asking — never pull facts from history itself, only from the context.
        - If the history and context conflict, trust the context.

        Formatting:
        - Use markdown: headings for multi-part answers, bullet points for lists, tables for comparisons.
        - Keep the answer as concise as possible while fully answering the question.
        - No preamble like "Based on the context provided" — answer directly.

        Conversation History: {history}
        Context: {context}
        Question: {query}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You answer questions using only the provided context."
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        stream=True
    )

    for chunk in response:
        token = chunk.choices[0].delta.content

        if token:
            yield token
