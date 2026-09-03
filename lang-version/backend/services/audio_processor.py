from bson import ObjectId
from bson.errors import InvalidId

from datetime import datetime, UTC
import tempfile
import os

from fastapi import HTTPException

from database import (
    documents_collection,
    knowledge_chunks_collection
)

from core.supabase import supabase

from utils.audio import transcribe_audio, create_audio_chunks
from utils.embedder import create_embeddings
from utils.keywords import extract_keywords

def process_audio(document_id: str):
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

    print("AUDIO PROCESSING STARTED:", document_id)

    documents_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "processing",
                "updatedAt": datetime.now(UTC)
            }
        }
    )

    storage_path = f"documents/{document['fileName']}"

    try:
        # 1. Download from Supabase
        print("DOWNLOADING AUDIO FROM SUPABASE")

        file_bytes = supabase.storage.from_("airw-documents").download(storage_path)

        print("AUDIO DOWNLOADED:", len(file_bytes), "bytes")

        suffix = os.path.splitext(document['fileName'])[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file_bytes)
            file_path = temp_file.name

        # 2. Transcribe audio

        print("STARTING TRANSCRIPTION")

        transcript = transcribe_audio(file_path)

        print("TRANSCRIPTION COMPLETE")

        # 3. Document → Chunks

        print("CREATING CHUNKS")

        chunks = create_audio_chunks(transcript)

        print("Chunks created:", len(chunks))

        # 4. Chunk -> Embedding -> MongoDB

        BATCH_SIZE = 20

        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[batch_start:batch_start + BATCH_SIZE]

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

            embeddings = create_embeddings(texts)

            batch_documents = []

            for index, chunk in enumerate(valid_chunks):
                text = chunk.page_content

                batch_documents.append({
                    "ownerId": document["ownerId"],
                    "collectionId": document["collectionId"],
                    "documentId": document_id,
                    "documentName": document["originalName"],
                    "fileName": document["fileName"],
                    "documentType": "audio",

                    "keywords": extract_keywords(text),
                    "chunkIndex": batch_start + index,
                    "text": text,

                    "startTime": chunk.metadata["startTime"],

                    "embedding": embeddings[index],
                    "createdAt": datetime.now(UTC),
                })

            # Insert this batch into MongoDB
            if batch_documents:
                knowledge_chunks_collection.insert_many(batch_documents)

        # 6. Mark document as ready

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
        print(f"Error processing audio document {document_id}: {e}")

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
            status_code=500,
            detail=f"Error processing audio document: {str(e)}"
        )

    finally:
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)