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

# import os
# import requests
# from langchain_core.documents.compressor import BaseDocumentCompressor

# RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
# RERANK_URL = f"https://router.huggingface.co/hf-inference/models/{RERANK_MODEL}"


# class HFAPIReranker(BaseDocumentCompressor):
#     top_n: int = 5

#     def compress_documents(self, documents, query, callbacks=None):
#         if not documents:
#             return []

#         headers = {
#             "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
#             "Content-Type": "application/json"
#         }

#         # Hugging Face Inference API batch format for pair classification
#         payload = {
#             "inputs": [
#                 {
#                     "text": query,
#                     "text_pair": doc.page_content,
#                 }
#                 for doc in documents
#             ]
#         }

#         response = requests.post(RERANK_URL, headers=headers, json=payload)
#         response.raise_for_status()

#         results = response.json()

#         scored = []
#         for doc, result in zip(documents, results):
#             # Parse response safely regardless of whether HF returns dict or list
#             if isinstance(result, list) and len(result) > 0:
#                 score = result[0].get("score", 0)
#             elif isinstance(result, dict):
#                 score = result.get("score", 0)
#             else:
#                 score = 0

#             scored.append((score, doc))

#         # Sort documents by highest score first
#         scored.sort(key=lambda x: x[0], reverse=True)

#         print(f"\nSuccessfully reranked {len(scored)} documents.")
#         return [doc for _, doc in scored[:self.top_n]]


# def get_reranker():
#     return HFAPIReranker(top_n=5)