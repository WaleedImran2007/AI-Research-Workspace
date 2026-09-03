import os
import time
import requests

from concurrent.futures import ThreadPoolExecutor

from langchain_core.documents.compressor import BaseDocumentCompressor
from pydantic import PrivateAttr


RERANK_MODEL = "BAAI/bge-reranker-v2-m3"

RERANK_URL = (
    f"https://router.huggingface.co/"
    f"hf-inference/models/{RERANK_MODEL}"
)

# Relative threshold.
# Example:
# best score = 0.60
# cutoff = 0.12
# keep scores >= 0.12
RELATIVE_THRESHOLD = 0.20

# Maximum number of chunks passed to the LLM
MAX_CHUNKS = 10

# Number of documents sent to HF in one request
BATCH_SIZE = 10

# Request timeout
REQUEST_TIMEOUT = 30

# Number of retries
MAX_RETRIES = 3

# Delay before retry
RETRY_BASE_DELAY = 2

MAX_WORKERS = 5


class HFAPIReranker(BaseDocumentCompressor):

    _session: requests.Session = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Reuse HTTP connections
        self._session = requests.Session()

    def _score_one(self, query, doc, headers):

        payload = {
            "inputs": [
                {
                    "text": query,
                    "text_pair": doc.page_content
                }
            ]
        }

        for attempt in range(MAX_RETRIES):

            try:

                response = self._session.post(
                    RERANK_URL,
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )

                response.raise_for_status()

                result = response.json()

                if result and result[0]:

                    return result[0][0]["score"]

                return 0

            except requests.exceptions.HTTPError as e:

                # Retry temporary gateway errors
                if response.status_code in (502, 503, 504):

                    if attempt < MAX_RETRIES - 1:

                        print(
                            f"⚠️ Hugging Face returned "
                            f"{response.status_code}. "
                            f"Retrying "
                            f"({attempt + 1}/{MAX_RETRIES})..."
                        )

                        time.sleep(2 ** attempt)

                        continue

                raise e

            except requests.exceptions.Timeout:

                if attempt < MAX_RETRIES - 1:

                    print(
                        f"⚠️ Hugging Face request timed out. "
                        f"Retrying "
                        f"({attempt + 1}/{MAX_RETRIES})..."
                    )

                    time.sleep(2 ** attempt)

                    continue

                raise

            except requests.exceptions.RequestException:

                if attempt < MAX_RETRIES - 1:

                    print(
                        f"⚠️ Hugging Face request failed. "
                        f"Retrying "
                        f"({attempt + 1}/{MAX_RETRIES})..."
                    )

                    time.sleep(2 ** attempt)

                    continue

                raise

        return 0

    def compress_documents(
        self,
        documents,
        query,
        callbacks=None
    ):

        if not documents:
            return []

        headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
            "Content-Type": "application/json",
        }

        # --------------------------------------------------
        # PARALLEL RERANKING
        # --------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            scores = list(
                executor.map(
                    lambda doc: self._score_one(
                        query,
                        doc,
                        headers
                    ),
                    documents
                )
            )

        # --------------------------------------------------
        # SORT DOCUMENTS BY SCORE
        # --------------------------------------------------

        scored = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True
        )

        # Debug output
        for score, doc in scored:

            print(
                f"{score:.4f} | "
                f"{doc.page_content[:100]}"
            )

        if not scored:
            return []

        # --------------------------------------------------
        # RELATIVE THRESHOLD
        # --------------------------------------------------

        best_score = scored[0][0]

        relative_cutoff = (
            best_score * RELATIVE_THRESHOLD
        )

        print(
            f"Best reranker score: "
            f"{best_score:.4f}"
        )

        print(
            f"Relative cutoff: "
            f"{relative_cutoff:.4f}"
        )

        filtered = [
            (score, doc)
            for score, doc in scored
            if score >= relative_cutoff
        ]

        # --------------------------------------------------
        # MAX CHUNKS
        # --------------------------------------------------

        filtered = filtered[:MAX_CHUNKS]

        print(
            f"Reranked {len(scored)} documents. "
            f"Kept {len(filtered)} documents."
        )

        return [
            doc
            for _, doc in filtered
        ]


def get_reranker():
    return HFAPIReranker()