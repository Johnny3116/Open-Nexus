"""Layered retrieval (Phase 1) — frozen core + FTS top-k + vector top-k.

Per turn: Layer-1 core memory (curated, capped) + top-k full-text matches +
top-k vector matches on the current query, deduped and summarised back into the
loop instead of stuffing the whole transcript in. Phase 0 uses only
``MemoryStore.recent``; this is the richer Supabase-backed path.
"""

from __future__ import annotations

from pydantic import BaseModel


class Recall(BaseModel):
    message_id: str
    content: str
    score: float
    via: str  # 'fts' | 'vector' | 'core'


class Retriever:
    def __init__(self, *, store, fts_top_k: int = 8, vector_top_k: int = 8) -> None:
        self.store = store
        self.fts_top_k = fts_top_k
        self.vector_top_k = vector_top_k

    def retrieve(self, *, session_id: str, query: str) -> list[Recall]:
        # TODO(phase-1): FTS + vector search, merge + dedupe by id, summarise.
        raise NotImplementedError("Retriever.retrieve: Phase 1")
