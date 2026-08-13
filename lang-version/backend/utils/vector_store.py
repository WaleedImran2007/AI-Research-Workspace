from langchain_mongodb import MongoDBAtlasVectorSearch

from database import knowledge_chunks_collection
from utils.embedder import get_model

vector_store = None

def get_vector_store():
    global vector_store

    if vector_store is None:
        embeddings = get_model()

        vector_store = MongoDBAtlasVectorSearch(
            collection=knowledge_chunks_collection,
            embedding=embeddings,
            index_name="vector_index",
            text_key="text",
            embedding_key="embedding",
        )

    return vector_store