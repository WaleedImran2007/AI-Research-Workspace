from schemas.collection import CollectionCreate, CollectionResponse
from fastapi import APIRouter, Depends, HTTPException

from middlewares.authMiddleware import get_current_user
from utils.serializer import collection_serializer, collections_serializer

from database import collections_collection, documents_collection, knowledge_chunks_collection, page_layouts_collection

from pymongo import ReturnDocument

from bson import ObjectId

from datetime import datetime, UTC

router = APIRouter()

# CREATE COLLECTION
@router.post("/", response_model=CollectionResponse)
def create_collection(
    collection: CollectionCreate,
    current_user: dict = Depends(get_current_user)
):
    new_collection = {
        "name": collection.name,
        "description": collection.description,
        "ownerId": current_user["id"],
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }

    result = collections_collection.insert_one(new_collection)

    created_collection = collections_collection.find_one({"_id": result.inserted_id})

    return collection_serializer(created_collection)

# GET ONLY OWN COLLECTIONS
@router.get("/", response_model=list[CollectionResponse])
def get_own_collections(current_user: dict = Depends(get_current_user)):
    users_collections = collections_collection.find({"ownerId": current_user["id"]})

    return collections_serializer(list(users_collections))

# GET ONLY OWN COLLECTION BY ID
@router.get("/{collection_id}", response_model=CollectionResponse)
def get_own_collection(
    current_user: dict = Depends(get_current_user),
    collection_id: str = None
):
    try:
        object_id = ObjectId(collection_id)
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid collection id"
        )

    collection = collections_collection.find_one({"_id": object_id, "ownerId": current_user["id"]})

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found or you do not have permission to view it.")

    return collection_serializer(collection)

# UPDATE ONLY OWN COLLECTION
@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: str,
    updated_collection: CollectionCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        object_id = ObjectId(collection_id)
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid collection id"
        )
    
    updated_collection = collections_collection.find_one_and_update(
        {"_id": object_id, "ownerId": current_user["id"]},
        { "$set": {
                "name": updated_collection.name,
                "description": updated_collection.description,
                "updatedAt": datetime.now(UTC)
            }
        },

        return_document=ReturnDocument.AFTER
    )

    if not updated_collection:
        raise HTTPException(status_code=404, detail="Collection not found or you do not have permission to update it.")
    
    return collection_serializer(updated_collection)

# DELETE ONLY OWN COLLECTION AND IT'S DOCUMENTS AND KNOWLEDGE CHUNKS
@router.delete("/{collection_id}", response_model=CollectionResponse)
def delete_collection(
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        object_id = ObjectId(collection_id)
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid collection id"
        )

    deleted_collection = collections_collection.find_one_and_delete(
        {"_id": object_id, "ownerId": current_user["id"]}
    )

    if not deleted_collection:
        raise HTTPException(status_code=404, detail="Collection not found or you do not have permission to delete it.")

    deleted_documents = documents_collection.delete_many({"collectionId": collection_id, "ownerId": current_user["id"]})
    
    deleted_chunks = knowledge_chunks_collection.delete_many({"collectionId": collection_id, "ownerId": current_user["id"]})

    deleted_page_layouts = page_layouts_collection.delete_many({"collectionId": collection_id, "ownerId": current_user["id"]})

    return collection_serializer(deleted_collection)
