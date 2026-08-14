from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

reranker = None

def get_reranker():
    global reranker

    if reranker is None:
        print("Loading Reranker Model...")

        # Limit torch's internal thread pool - reduces resident memory used
        # by the BLAS/OMP threads without changing reranking output.
        import torch
        torch.set_num_threads(1)

        model = HuggingFaceCrossEncoder(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
            model_kwargs={
                "device": "cpu"
            }
        )

        reranker = CrossEncoderReranker(
            model=model, 
            top_n=5
        )

    return reranker