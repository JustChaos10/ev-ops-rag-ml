"""Utilities for lightweight retrieval over the in-memory knowledge base."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class RetrievedDocument:
    doc_id: str
    text: str
    score: float
    tags: Sequence[str]


class SimpleRetriever:
    """Minimal TF-IDF retriever for the EV knowledge base."""

    def __init__(self, documents: Iterable[dict]) -> None:
        docs = list(documents)
        if not docs:
            raise ValueError("Retriever requires at least one document")

        self._documents = docs
        self._vectorizer = TfidfVectorizer(stop_words="english")
        corpus = [doc["text"] for doc in docs]
        self._doc_matrix = self._vectorizer.fit_transform(corpus)

    def fetch_top_k(self, query: str, k: int = 3) -> List[RetrievedDocument]:
        query_vec = self._vectorizer.transform([query])
        # Cosine similarity simplifies to dot product with normalized tf-idf vectors.
        scores = (self._doc_matrix @ query_vec.T).toarray().ravel()
        top_indices = np.argsort(scores)[::-1][:k]

        results: List[RetrievedDocument] = []
        for idx in top_indices:
            doc = self._documents[int(idx)]
            score = float(scores[int(idx)])
            if score <= 0:
                continue
            results.append(
                RetrievedDocument(
                    doc_id=doc["id"],
                    text=doc["text"],
                    score=score,
                    tags=tuple(doc.get("tags", [])),
                )
            )
        return results

