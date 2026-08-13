from bson import ObjectId
from bson.errors import InvalidId
from database import (
    documents_collection,
    knowledge_chunks_collection,
    page_layouts_collection,
)

from fastapi import HTTPException
import os

from datetime import datetime, UTC

from utils.pdf import extract_text
from utils.splitter import create_chunks
from utils.embedder import create_embeddings
from utils.keywords import extract_keywords


def process_document(document_id: str):
    try:
        object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID format."
        )

    document = documents_collection.find_one({"_id": object_id})

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    documents_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "processing",
                "updatedAt": datetime.now(UTC)
            }
        }
    )

    file_path = os.path.join(
        "uploads/documents",
        document["fileName"]
    )

    if not os.path.exists(file_path):
        documents_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "failed",
                    "updatedAt": datetime.now(UTC)
                }
            }
        )

        raise HTTPException(
            status_code=404,
            detail="Document file not found."
        )

    try:
        # Step 1: PDF -> LangChain Documents
        pages = extract_text(file_path)

        for page in pages:
            if not page.page_content.strip():
                continue

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

        # Step 2: LangChain Documents -> Chunks
        chunks = create_chunks(pages)

        # Step 3: Chunk -> Embedding -> MongoDB
        BATCH_SIZE = 20

        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[
                batch_start:batch_start + BATCH_SIZE
            ]

            # Remove empty chunks
            valid_chunks = [
                chunk
                for chunk in batch_chunks
                if chunk.page_content.strip()
            ]

            if not valid_chunks:
                continue

            texts = [
                chunk.page_content
                for chunk in valid_chunks
            ]

            # Generate embeddings for the whole batch
            embeddings = create_embeddings(texts)

            batch_documents = []

            for index, chunk in enumerate(valid_chunks):
                text = chunk.page_content

                embedding = embeddings[index]
                keywords = extract_keywords(text)

                batch_documents.append({
                    "ownerId": document["ownerId"],
                    "collectionId": document["collectionId"],
                    "documentId": document_id,
                    "documentName": document["originalName"],
                    "fileName": document["fileName"],

                    "page": chunk.metadata["page"],
                    "keywords": keywords,

                    "chunkIndex": batch_start + index,
                    "text": text,
                    "embedding": embedding,

                    "createdAt": datetime.now(UTC),
                })

            # Insert this batch into MongoDB
            if batch_documents:
                knowledge_chunks_collection.insert_many(
                    batch_documents
                )

        # Step 4: Mark document as ready
        documents_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "ready",
                    "updatedAt": datetime.now(UTC)
                }
            }
        )

    except Exception as e:
        print("Document processing error:", e)

        documents_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "failed",
                    "updatedAt": datetime.now(UTC)
                }
            }
        )
