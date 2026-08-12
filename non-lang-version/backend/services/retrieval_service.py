from utils.embedder import create_embedding
from database import knowledge_chunks_collection
from utils.similarity import cosine_similarity

# from services.keyword_search import keyword_search
from services.bm25_search import bm25_search
from services.reranker import rerank

from schemas.filter import FilterSchema

def search_chunks(filters: FilterSchema, owner_id: str):
    TOP_K = 20

    query_embedding = create_embedding(filters.query)

    mongo_filter = {
        "ownerId": owner_id
    }

    if filters.collection_ids:
        mongo_filter["collectionId"] = {"$in": filters.collection_ids}

    if filters.document_ids:
        mongo_filter["documentId"] = {"$in": filters.document_ids}

    if filters.pages:
        mongo_filter["page"] = {"$in": filters.pages}

    chunks = list(knowledge_chunks_collection.find(mongo_filter))

    scored_chunks = []

    for chunk in chunks:
        similarity = cosine_similarity(query_embedding, chunk["embedding"])

        scored_chunks.append({
            "score": similarity,
            "chunk": chunk
        })

    scored_chunks.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    vector_results = scored_chunks[:TOP_K]

    bm25_results = bm25_search(filters.query, owner_id, filters.collection_ids)

    # Add vector search results to merged_results
    RRF_K = 60

    rrf_scores = {}

    for rank, item in enumerate(vector_results, start=1):
        chunk_id = str(item["chunk"]["_id"])

        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = {
                "score": 0,
                "chunk": item["chunk"]
            }

        rrf_scores[chunk_id]["score"] += 1 / (RRF_K + rank)

    for rank, item in enumerate(bm25_results, start=1):
        chunk_id = str(item["chunk"]["_id"])

        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = {
                "score": 0,
                "chunk": item["chunk"]
            }

        rrf_scores[chunk_id]["score"] += 1 / (RRF_K + rank)

    # Convert the RRF scores to a list and sort by score
    merged_results = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)

    return rerank(filters.query, merged_results[:20])