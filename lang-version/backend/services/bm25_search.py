import os
from collections import OrderedDict

from database import knowledge_chunks_collection
from utils.keywords import extract_keywords

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

# Each cached retriever holds the full text corpus for an owner/collection
# in memory. Left unbounded, this cache grows forever as more distinct
# owner/collection combinations are queried over the app's lifetime, which
# is a common cause of memory slowly climbing until the process gets OOM
# killed. We bound it to a max number of entries and evict the least
# recently used one once the limit is reached. Behavior/results returned by
# get_bm25_retriever are unchanged - only how long a built index stays
# cached differs.
BM25_CACHE_MAX_SIZE = int(os.environ.get("BM25_CACHE_MAX_SIZE", "2"))

bm25_cache: "OrderedDict" = OrderedDict()

def clear_bm25_cache(
    owner_id: str,
    collection_ids: list[str] | None = None
):
    keys_to_remove = []

    for key in bm25_cache.keys():

        cached_owner, cached_collections = key

        if cached_owner != owner_id:
            continue

        if (
            collection_ids
            and cached_collections != tuple(collection_ids)
        ):
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

        # mark as most-recently-used
        bm25_cache.move_to_end(cache_key)

        return retriever

    print("Building BM25 retriever...")

    mongo_filter = {
        "ownerId": owner_id,
    }

    if collection_ids:
        mongo_filter["collectionId"] = {"$in": collection_ids}

    projection = {
        "_id": 1,
        "text": 1,
        "ownerId": 1,
        "collectionId": 1,
        "documentId": 1,
        "chunkIndex": 1,
    }

    chunks = list(knowledge_chunks_collection.find(
        mongo_filter, 
        projection
    ))

    docs = []

    for chunk in chunks:
        docs.append(
            Document(
                page_content = chunk["text"],
                metadata={
                    "_id": str(chunk["_id"]),
                    "ownerId": chunk.get("ownerId"),
                    "collectionId": chunk.get("collectionId"),
                    "documentId": chunk.get("documentId"),
                    "chunkIndex": chunk.get("chunkIndex"),
                }
            )
        )

    # We don't need MongoDB chunks anymore.
    del chunks

    if not docs:
        return None

    bm25_retriever = BM25Retriever.from_documents(
        docs,
        preprocess_func=extract_keywords,
    )

    bm25_retriever.k = k

    # save in cache, evicting the oldest/least-recently-used entry if we're at capacity
    if len(bm25_cache) >= BM25_CACHE_MAX_SIZE:
        evicted_key, _ = bm25_cache.popitem(last=False)
        print(f"BM25 cache full, evicted least-recently-used entry: {evicted_key}")

    bm25_cache[cache_key] = bm25_retriever

    return bm25_retriever