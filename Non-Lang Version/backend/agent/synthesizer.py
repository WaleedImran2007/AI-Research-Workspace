from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_context(context: dict):
    """
    Aggregates ToolResult objects into:

    - One large context string for the LLM
    - One merged list of sources for the frontend
    """

    context_parts = []
    sources = []
    seen_sources = set()

    for tool_name, tool_result in context.items():
        if tool_result is None:
            continue

        # Tool Failed
        if isinstance(tool_result, dict) and "error" in tool_result:
            context_parts.append(f"[{tool_name} Error]\n{tool_result['error']}")
            continue

        # Ignore unexpected return types
        if not hasattr(tool_result, "llm_context"):
            continue

        # llm_context
        if tool_result.llm_context:
            context_parts.append(tool_result.llm_context.strip())

        # sources
        if tool_result.sources:
            for source in tool_result.sources:
                source_key = (
                    source.documentId,
                    source.page,
                )

                if source_key in seen_sources:
                    continue

                seen_sources.add(source_key)

                # Convert Source into dict for serialization
                sources.append(source.model_dump())

    return "\n\n".join(context_parts), sources



def synthesize(user_query: str, context: dict, history: str = "", reflection: dict = None):
    """
    Generates the final answer using all ToolResults.

    Assumes the caller has already validated the plan/context via reflection
    before calling this function; `reflection` is accepted for future use
    but is not currently referenced here.

    Returns: (stream_generator, sources)
    """

    context_text, sources = build_context(context)

    if not context_text.strip():
        def _empty_stream():
            yield "I couldn't find any relevant information to answer your question."

        return _empty_stream(), sources

    prompt = f"""
        You are an AI assistant that answers questions using only the information provided in <context> below.

        <context>
        {context_text}
        </context>

        <conversation_history>
        {history}
        </conversation_history>

        <question>
        {user_query}
        </question>

        ## Grounding rules
        - Answer using only the information in <context>. Never use outside knowledge, and never invent facts, numbers, or code that isn't supported by it.
        - Use <conversation_history> only to resolve references ("it", "that", "the previous one") so you understand what's being asked — never pull facts or numbers from history, only from <context>.
        - If <context> and <conversation_history> conflict, trust <context>.
        - If <context> has no relevant information, reply with exactly: "I could not find the answer to your question in the provided context."
        - If <context> only partially answers the question, answer what you can and clearly state what's missing.
        - If <context> contains a successful result, answer confidently and directly, as a stated fact — do not hedge, qualify, or present it as a hypothetical or example.
        - Never say you couldn't find an answer if <context> clearly contains a successful result.
        - Never say the context say it. Be confident in your answer, and present it as though you directly know it, calculated it, or read the document yourself.

        ## Presentation rules
        - Never mention internal context, retrieval, tools, planners, or Python execution — present everything as though you directly know it, calculated it, or read the document yourself.
        - If the question asks for code: show the code first, in a fenced block with the correct language tag, then a brief explanation if useful.
        - If the question asks for an explanation: explain first; only show supporting calculations/data afterward if it adds value.
        - If the question asks for a calculation: give the final answer first, then show the working underneath if helpful.
        - If the context indicates an image/graph was generated, mention once that it's attached — don't describe it in detail unless asked.
        - Do not say you couldn't find an answer if <context> clearly contains a successful result.

        ## Formatting
        - Markdown: headings for multi-part answers, bullet points for lists, tables for comparisons.
        - No preamble like "Based on the context provided" — answer directly.
        - Be as concise as possible while fully answering the question. Don't repeat the same information twice.
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

    def _stream():
        for chunk in response:
            if not chunk.choices:
                continue

            token = chunk.choices[0].delta.content

            if token:
                yield token

    return _stream(), sources