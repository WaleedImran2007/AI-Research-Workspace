from services.retrieval_service import search_chunks
from schemas.tool_result import ToolResult

def execute(filters, owner_id, input = None):
    chunks = search_chunks(
        filters=filters,
        owner_id=owner_id
    )

    print("Retrieved Chunks:", chunks)

    llm_context = ""
    sources = []
    seen_sources = set()

    for item in chunks:
        chunk = item["chunk"]

        llm_context += chunk["text"] + "\n\n"

        source_key = (chunk["documentId"], chunk.get("page"))

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            sources.append({
                "type": "document",
                "documentId": chunk["documentId"],
                "documentName": chunk.get("documentName", "Unknown Document"),
                "fileName": chunk.get("fileName", "Unknown File"),
                "page": chunk.get("page"),
                "text": chunk["text"]
            })

    return ToolResult(
        llm_context=llm_context.strip(),
        sources=sources
    )