from services.retrieval_service import search_chunks
from schemas.tool_result import ToolResult

from langchain_core.tools import tool

@tool
def retrieval(filters, owner_id, input = None) -> ToolResult:
    """Retrieves relevant chunks of text based on the provided filters and owner ID."""

    chunks = search_chunks(
        filters=filters,
        owner_id=owner_id
    )

    llm_context = ""
    sources = []
    seen_sources = set()

    for doc in chunks:
        chunk = doc.metadata

        llm_context += doc.page_content + "\n\n"

        source_key = (
            chunk["documentId"],
            chunk.get("documentType"),
            chunk.get("page"),
            chunk.get("chunkIndex")
        )

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            sources.append({
                "type": "document",
                "documentId": chunk["documentId"],
                "documentName": chunk.get("documentName", "Unknown Document"),
                "fileName": chunk.get("fileName", "Unknown File"),
                "documentType": chunk.get("documentType"),
                "page": chunk.get("page"),
                "startTime": chunk.get("startTime"),
                "text": doc.page_content
            })

    return ToolResult(
        llm_context=llm_context.strip(),
        sources=sources or []
    )