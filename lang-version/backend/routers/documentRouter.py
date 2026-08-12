from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from database import documents_collection, collections_collection, page_layouts_collection
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, UTC

from schemas.document import DocumentResponse
from utils.serializer import document_serializer, documents_serializer

from middlewares.authMiddleware import get_current_user
import os
import time

from services.document_processor import process_document
from services.bm25_search import clear_bm25_cache

from fastapi import BackgroundTasks

router = APIRouter()

UPLOAD_FOLDER = "uploads/documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure the upload folder exists

ALLOWED_FILE_TYPES = [
    "application/pdf",
    "text/csv"
]

DOCUMENT_TYPES = {
    "application/pdf": "pdf",
    "text/csv": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
}

# Upload a document to a specific collection
@router.post("/{collection_id}")
async def upload_document(
    collection_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    collection = collections_collection.find_one({"_id": ObjectId(collection_id), "ownerId": current_user["id"]})

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found or you do not have permission to upload to this collection.")

    # Validate file type (later we'll support other formats)
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Only files of type {', '.join(ALLOWED_FILE_TYPES)} are allowed."
        )

    # Read file
    contents = await file.read()

    # Generate a unique filename
    stored_name = f"{int(time.time())}_{file.filename}"

    # SAVE FILE
    file_path = os.path.join(UPLOAD_FOLDER, stored_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    document_type = DOCUMENT_TYPES.get(file.content_type)

    # Save document in database
    new_document = {
        "ownerId": current_user["id"],
        "collectionId": collection_id,
        "originalName": file.filename,
        "fileName": stored_name,
        "mimeType": file.content_type,
        "documentType": document_type,
        "filesize": len(contents),
        "status": "uploaded",
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }

    if document_type == "csv":
        new_document["status"] = "ready"  # CSV files are ready immediately
    elif document_type == "pdf":
        new_document["status"] = "processing"  # PDFs will be processed in the background


    result = documents_collection.insert_one(new_document)

    # clear the BM25 cache for this owner and collection since a new document has been added

    clear_bm25_cache(current_user["id"], [collection_id])

    if file.content_type == "application/pdf":
        background_tasks.add_task(
            process_document, 
            str(result.inserted_id)
        )

    return {
        "message": f"Document uploaded successfully. { 'Processing started in the background.' if file.content_type == 'application/pdf' else 'No background processing required.' }",
        "documentId": str(result.inserted_id),
    }


# Get all documents of a certain collection
@router.get("/{collection_id}", response_model=list[DocumentResponse])
def get_documents(
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    collection = collections_collection.find_one( {"_id": ObjectId(collection_id), "ownerId": current_user["id"]} )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found or you do not have permission to view documents in this collection.")

    documents = documents_collection.find({"collectionId": collection_id, "ownerId": current_user["id"]})

    return documents_serializer(list(documents))

# Get a specific document by its ID
@router.get("/document/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    document = documents_collection.find_one({"_id": object_id, "ownerId": current_user["id"]})

    if not document:
        raise HTTPException(status_code=404, detail="Document not found or you do not have permission to view this document.")

    return document_serializer(document)

# Delete a specific document by its ID
@router.delete("/document/{document_id}")
def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        object_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    document = documents_collection.find_one({"_id": object_id, "ownerId": current_user["id"]})

    if not document:
        raise HTTPException(status_code=404, detail="Document not found or you do not have permission to delete this document.")

    # Delete the file from the filesystem
    file_path = os.path.join(UPLOAD_FOLDER, document["fileName"])

    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the document from the database
    documents_collection.delete_one({"_id": object_id})

    # clear the BM25 cache for this owner and collection since a document has been deleted

    clear_bm25_cache(current_user["id"], [document["collectionId"]])

    return {
        "message": "Document deleted successfully"
    }    

# Open the pdf/document in the browser
@router.get("/{document_id}/view")
def view_document(
    document_id: str
):
    try:
        obj_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    document = documents_collection.find_one({"_id": obj_id})

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = os.path.join(UPLOAD_FOLDER, document["fileName"])

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on the server.")

    # content_disposition_type="inline" tells the browser to open it in-browser rather than downloading
    return FileResponse(
        path=file_path,
        media_type=document.get("mimeType", "application/pdf"),
        content_disposition_type="inline" 
    )

# GET THE SPANS
@router.get("/{document_id}/layout/{page_number}")
def get_page_layout(
    document_id: str,
    page_number: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    document = documents_collection.find_one({"_id": obj_id, "ownerId": current_user["id"]})

    if not document:
        raise HTTPException(status_code=404, detail="Document not found or you do not have permission to view this document.")

    page_layout = page_layouts_collection.find_one({
        "documentId": document_id,
        "page": page_number
    })

    if not page_layout:
        raise HTTPException(status_code=404, detail="Page layout not found.")

    return {
        "page": page_layout["page"],
        "spans": page_layout["spans"]
    }
