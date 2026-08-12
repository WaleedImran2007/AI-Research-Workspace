from bson import ObjectId
from bson.errors import InvalidId
from database import documents_collection, knowledge_chunks_collection, page_layouts_collection

from fastapi import HTTPException
import os

from datetime import datetime, UTC

from utils.pdf import extract_text
from utils.splitter import create_chunks
from utils.embedder import create_embedding
from utils.keywords import extract_keywords

def process_document(document_id: str):
    try:
        object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    document = documents_collection.find_one({"_id": object_id})

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    documents_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "processing",
                "updatedAt": datetime.now(UTC)
            }
        }
    )

    file_path = os.path.join("uploads/documents", document["fileName"])

    if not os.path.exists(file_path):
        documents_collection.update_one(
            {"_id": object_id},
            {"$set": {"status": 'failed', "updatedAt": datetime.now(UTC)}}
        )
        raise HTTPException(status_code=404, detail="Document file not found.")

    try:
        # Step 1: PDF -> Langchain Documents
        pages = extract_text(file_path)

        for page in pages:
            if not page.page_content.strip():
                continue  # Skip empty pages

            # Save page layout
            page_layouts_collection.insert_one({
                "ownerId": document["ownerId"],
                "collectionId": document["collectionId"],
                "documentId": document_id,
                "page": page.metadata["page"],
                "spans": page.metadata["spans"],
                "width": page.metadata["width"],
                "height": page.metadata["height"],
                "createdAt": datetime.now(UTC),
            })

            # Step 2: Langchain Document -> Chunks
            chunks = create_chunks(pages)

            chunks_to_insert = []

            # Step 3: Chunk -> Embedding -> MongoDB
            for index, chunk in enumerate(chunks):
                text = chunk.page_content

                if not text.strip():
                    continue  # Skip empty chunks

                embedding = create_embedding(text)
                keywords = extract_keywords(text)

                chunks_to_insert.append({
                    "ownerId": document["ownerId"],
                    "collectionId": document["collectionId"],
                    "documentId": document_id,
                    "documentName": document["originalName"],
                    "fileName": document["fileName"],

                    "page": chunk.metadata["page"],
                    "keywords": keywords,

                    "chunkIndex": index,
                    "text": text,
                    "embedding": embedding,
                    "createdAt": datetime.now(UTC),
                })

        if chunks_to_insert:
            knowledge_chunks_collection.insert_many(chunks_to_insert)

        documents_collection.update_one(
            {"_id": object_id},
            {"$set": {"status": 'ready', "updatedAt": datetime.now(UTC)}}
        )

    except Exception as e:
        print("Document processing error:", e)

        documents_collection.update_one(
            {"_id": object_id},
            {"$set": {"status": 'failed', "updatedAt": datetime.now(UTC)}}
        )
