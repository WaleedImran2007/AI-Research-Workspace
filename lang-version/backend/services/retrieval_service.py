from utils.vector_store import vector_store

# from services.keyword_search import keyword_search
from services.bm25_search import get_bm25_retriever
from services.reranker import reranker

from schemas.filter import FilterSchema

from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever


def search_chunks(filters: FilterSchema, owner_id: str):
    TOP_K = 20

    vector_filter = {
        "ownerId": owner_id,
    }

    if filters.collection_ids:
        vector_filter["collectionId"] = {"$in": filters.collection_ids}

    if filters.pages:
        vector_filter["page"] = {"$in": filters.pages}

    # Perform vector search
    vector_retriever = vector_store.as_retriever(
        search_kwargs={
            "k": TOP_K,
            "pre_filter": vector_filter
        }
    )

    bm25_retriever = get_bm25_retriever(owner_id, filters.collection_ids, k=TOP_K)

    base_retriever = None

    if bm25_retriever is None:
        base_retriever = vector_retriever
    else:
        base_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.5, 0.5],
            id_key="_id",
            c=60
        )

    # Use a ContextualCompressionRetriever to compress the retrieved documents

    compression_retriever = ContextualCompressionRetriever(
        base_compressor = reranker,
        base_retriever = base_retriever
    )

    return compression_retriever.invoke(filters.query)