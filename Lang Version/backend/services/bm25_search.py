from database import knowledge_chunks_collection
from utils.keywords import extract_keywords

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

bm25_cache = {}

def clear_bm25_cache(owner_id: str, collection_ids: list[str] | None = None):
    keys_to_remove = []

    for key in bm25_cache.keys():
        cached_owner, cached_collections = key

        if cached_owner != owner_id:
            continue

        if collection_ids and cached_collections != tuple(collection_ids):
            continue

        keys_to_remove.append(key)

    for key in keys_to_remove:
        del bm25_cache[key]

    print("BM25 cache cleared")


def get_bm25_retriever(owner_id: str, collection_ids: list[str] | None, k: int = 20):

    cache_key = (
        owner_id,
        tuple(collection_ids) if collection_ids else None,
    )

    # returned cached retriever if it exists
    if cache_key in bm25_cache:
        print("Using cached BM25 retriever")

        retriever = bm25_cache[cache_key]
        retriever.k = k

        return retriever

    print("Building BM25 retriever...")

    mongo_filter = {
        "ownerId": owner_id,
    }

    if collection_ids:
        mongo_filter["collectionId"] = {"$in": collection_ids}

    chunks = list(knowledge_chunks_collection.find(mongo_filter))

    docs = []

    for chunk in chunks:
        docs.append(
            Document(
                page_content = chunk["text"],
                metadata = {
                    **chunk,
                    "_id": str(chunk["_id"])
                }
            )
        )

    if not docs:
        return None

    bm25_retriever = BM25Retriever.from_documents(
        docs,
        preprocess_func=extract_keywords,
    )

    bm25_retriever.k = k

    # save in cache
    bm25_cache[cache_key] = bm25_retriever

    return bm25_retriever