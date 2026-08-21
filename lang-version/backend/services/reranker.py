import os
import requests
from concurrent.futures import ThreadPoolExecutor

from langchain_core.documents.compressor import BaseDocumentCompressor

RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
RERANK_URL = f"https://router.huggingface.co/hf-inference/models/{RERANK_MODEL}"

THRESHOLD_SCORE = 0.2
MAX_CHUNKS = 10


class HFAPIReranker(BaseDocumentCompressor):
    def _score_one(self, query, doc, headers):
        payload = {
            "inputs": [
                {
                    "text": query, 
                    "text_pair": doc.page_content
                }
            ]
        }

        response = requests.post(
            RERANK_URL, 
            headers=headers, 
            json=payload
        )

        response.raise_for_status()

        result = response.json()  # [[{"label": "...", "score": ...}]]

        return result[0][0]["score"] if result and result[0] else 0

    def compress_documents(self, documents, query, callbacks=None):
        if not documents:
            return []

        headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
            "Content-Type": "application/json",
        }

        # The batch endpoint silently returns only 1 result no matter how
        # many pairs are sent (confirmed by testing, undocumented) - so
        # each document is scored with its own request instead. Threaded
        # so 24 documents don't mean 24x sequential latency.
        with ThreadPoolExecutor(max_workers=8) as executor:
            scores = list(
                executor.map(lambda doc: self._score_one(query, doc, headers), documents)
            )

        scored = sorted(
            zip(scores, documents), 
            key=lambda x: x[0], 
            reverse=True
        )

        for score, doc in scored:
            print(f"{score:.4f} | {doc.page_content[:100]}")

        filtered = [
            (score, doc)
            for score, doc in scored
            if score >= THRESHOLD_SCORE
        ]

        print(f"Successfully reranked {len(scored)} documents.")

        return [
            doc 
            for _, doc in filtered[: MAX_CHUNKS]]


def get_reranker():
    return HFAPIReranker()