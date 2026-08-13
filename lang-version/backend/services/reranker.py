from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

reranker = None

def get_reranker():
    global reranker

    if reranker is None:
        print("Loading Reranker Model...")

        model = HuggingFaceCrossEncoder(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        reranker = CrossEncoderReranker(
            model=model, 
            top_n=5
        )

    return reranker