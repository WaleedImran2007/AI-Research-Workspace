from chains.synthesizer_chain import synthesizer_chain

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

    Returns: (stream_generator, sources)
    """

    context_text, sources = build_context(context)

    if not context_text.strip():
        def _empty_stream():
            yield "I couldn't find any relevant information to answer your question."

        return _empty_stream(), sources

    response = synthesizer_chain.stream(
        {
            "context_text": context_text,
            "history": history,
            "user_query": user_query
        }
    )


    def _stream():
        for chunk in response:
            if chunk.content:
                yield chunk.content

    return _stream(), sources