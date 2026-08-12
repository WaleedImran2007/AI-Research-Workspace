from database import knowledge_chunks_collection
from schemas.tool_result import ToolResult

def execute(filters, owner_id, input = None):
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
            x["page"],
            x["chunkIndex"]
        )
    )

    llm_context = ""
    sources = []
    seen_documents = set()

    for chunk in chunks:
        llm_context += chunk["text"].strip() + "\n\n"

        source_key = (chunk["documentId"], chunk.get("page"))

        if source_key not in seen_documents:
            seen_documents.add(source_key)
        
            sources.append({
                "type": "document",
                "documentId": chunk["documentId"],
                "documentName": chunk.get("documentName", "Unknown Document"),
                "fileName": chunk.get("fileName", "Unknown File"),
                "page": chunk.get("page", "Unknown Page"),
                "text": chunk["text"]
            })

    return ToolResult(
        llm_context=llm_context,
        sources=sources
    )