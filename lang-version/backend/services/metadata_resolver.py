from database import documents_collection, collections_collection
from schemas.filter import FilterSchema

def resolve_filters(filters: FilterSchema, owner_id: str) -> FilterSchema:
    document_ids = []
    collection_ids = []

    for document_name in filters.document_names:
        document = documents_collection.find_one({
            "originalName": {
                "$regex": document_name,
                "$options": "i"
            },

            "ownerId": owner_id
        })

        if document:
            document_ids.append(str(document["_id"]))

    for collection_name in filters.collection_names:
        collection = collections_collection.find_one({
            "name": {
                "$regex": collection_name,
                "$options": "i"
            }, 

            "ownerId": owner_id
        })

        if collection:
            collection_ids.append(str(collection["_id"]))

    return FilterSchema(
        query = filters.query,
        document_names = [],
        collection_names = [],
        pages = filters.pages,
        document_ids = document_ids,
        collection_ids = collection_ids
    )