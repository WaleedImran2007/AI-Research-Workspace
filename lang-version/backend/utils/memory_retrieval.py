from langchain_mongodb import MongoDBAtlasVectorSearch

from database import memories_collection
from utils.embedder import get_model

memory_vector_store = None

def get_memory_vector_store():
    global memory_vector_store

    if memory_vector_store is None:
        embeddings = get_model()

        memory_vector_store = MongoDBAtlasVectorSearch(
            collection=memories_collection,
            embedding=embeddings,
            index_name="memory_vector_index",
            text_key="memory_text",
            embedding_key="embedding"
        )

    return memory_vector_store

def retrieve_memories(
    user_query: str,
    owner_id: str,
    k: int = 5
):
    return get_memory_vector_store().similarity_search(
        query=user_query,
        k=k,
        pre_filter={
            "ownerId": owner_id
        }
    )