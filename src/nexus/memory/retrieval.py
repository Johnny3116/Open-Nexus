"""Layer-2 retrieval: FTS first, vectors second, deduped, summarised.

Per turn: top-k full-text matches + top-k vector matches on the current query,
merged and de-duplicated, then summarised back into the loop instead of stuffing
the whole transcript into context.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Recall:
    """A retrieved snippet with its provenance and score."""

    message_id: str
    content: str
    score: float
    via: str  # 'fts' | 'vector'


class Retriever:
    def __init__(self, *, store, embeddings, fts_top_k: int = 8, vector_top_k: int = 8) -> None:
        self.store = store
        self.embeddings = embeddings
        self.fts_top_k = fts_top_k
        self.vector_top_k = vector_top_k

    def retrieve(self, *, session, query: str) -> list[Recall]:
        # TODO(phase-1): run FTS (to_tsquery) and vector (cosine) searches,
        # merge + dedupe by message_id, keep best score, return ordered Recalls.
        raise NotImplementedError("Retriever.retrieve: Phase 1")
