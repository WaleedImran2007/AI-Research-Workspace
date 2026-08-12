from database import knowledge_chunks_collection
from utils.keywords import extract_keywords

def keyword_search(query: str, owner_id: str, collection_ids: list[str] | None = None):
    keywords = extract_keywords(query)

    mongo_filter = {
        "ownerId": owner_id,
        "keywords": {
            "$in": keywords
        }
    }

    if collection_ids:
        mongo_filter["collectionId"] = {"$in": collection_ids}

    results = list(knowledge_chunks_collection.find(mongo_filter))

    scored_results = []
    query_keywords = set(keywords)

    for chunk in results:
        chunks_keywords = set(chunk["keywords"])
        matched_keywords = query_keywords.intersection(chunks_keywords)

        bonus = 0.1 * len(matched_keywords)

        print("Matched:", matched_keywords)
        print("Bonus:", bonus)
        print("----------------")

        scored_results.append({
            "score": bonus,
            "chunk": chunk
        })

    return scored_results