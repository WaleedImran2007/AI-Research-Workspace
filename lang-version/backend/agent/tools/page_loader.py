from database import knowledge_chunks_collection
from schemas.tool_result import ToolResult

from langchain_core.tools import tool

@tool
def page_loader(filters, owner_id, input = None) -> ToolResult:
    """Retrieves relevant chunks of text based on the provided filters and owner ID. It is basically for large retriaval of documents and their chunks to answer questions such as summary, analysis, and other questions that require the entire document content. It is not used for retrieval of specific chunks of text based on filters."""

    mongo_filter = {
        "ownerId": owner_id
    }

    if filters.document_ids:
        mongo_filter["documentId"] = {"$in": filters.document_ids}

    if filters.collection_ids:
        mongo_filter["collectionId"] = {"$in": filters.collection_ids}

    if filters.pages:
        mongo_filter["page"] = {"$in": filters.pages}

    chunks = list(knowledge_chunks_collection.find(mongo_filter))

    chunks.sort(
        key=lambda x: (
            x.get("page") if x.get("page") is not None else x.get("startTime", 0),
            x["chunkIndex"]
        )
    )

    llm_context = ""
    sources = []
    seen_documents = set()

    for chunk in chunks:
        llm_context += chunk["text"].strip() + "\n\n"

        source_key = (
            chunk["documentId"],
            chunk.get("documentType"),
            chunk.get("page"),
            chunk.get("startTime"),
        )

        if source_key not in seen_documents:
            seen_documents.add(source_key)
        
            sources.append({
                "type": "document",
                "documentId": chunk["documentId"],
                "documentName": chunk.get("documentName", "Unknown Document"),
                "fileName": chunk.get("fileName", "Unknown File"),
                "documentType": chunk.get("documentType"),
                "page": chunk.get("page"),
                "startTime": chunk.get("startTime"),
                "text": chunk["text"]
            })

    return ToolResult(
        llm_context=llm_context,
        sources=sources or []
    )