from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, chunks: list): # chunks are top 20
    print("Reranking chunks...", len(chunks))
    pairs = []

    for item in chunks:
        pairs.append(
            (
                query,
                item["chunk"]["text"]
            )
        )

    scores = reranker.predict(pairs)

    reranked_chunks = []

    for item, score in zip(chunks, scores):
        reranked_chunks.append({
            "score": float(score),
            "chunk": item["chunk"]
        })

    reranked_chunks.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print("Reranked Chunks:", reranked_chunks[:5])

    return reranked_chunks[:5]