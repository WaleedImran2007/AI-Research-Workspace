from langchain_mongodb import MongoDBAtlasVectorSearch

from database import knowledge_chunks_collection
from utils.embedder import create_embedding, create_embeddings

class HuggingFaceAPIEmbedding:
    def embed_query(self, text: str) -> list[float]:
        return create_embedding(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return create_embeddings(texts)

vector_store = None

def get_vector_store():
    global vector_store

    if vector_store is None:
        embeddings = HuggingFaceAPIEmbedding()

        vector_store = MongoDBAtlasVectorSearch(
            collection=knowledge_chunks_collection,
            embedding=embeddings,
            index_name="vector_index",
            text_key="text",
            embedding_key="embedding",
        )

    return vector_store