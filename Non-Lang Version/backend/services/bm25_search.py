from rank_bm25 import BM25Okapi
from database import knowledge_chunks_collection
from utils.keywords import extract_keywords

def bm25_search(query: str, owner_id: str, collection_ids: list[str] | None = None):
    mongo_filter = {
        "ownerId": owner_id,
    }

    if collection_ids:
        mongo_filter["collectionId"] = {"$in": collection_ids}

    chunks = list(knowledge_chunks_collection.find(mongo_filter))

    corpus = []

    for chunk in chunks:
        corpus.append(chunk["keywords"])

    bm25 = BM25Okapi(corpus)
    query_keywords = extract_keywords(query)
    scores = bm25.get_scores(query_keywords)

    scored_results = []

    for chunk, score in zip(chunks, scores):
        if score <= 0:
            continue

        scored_results.append({
            "score": score,
            "chunk": chunk
        })

    scored_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored_results