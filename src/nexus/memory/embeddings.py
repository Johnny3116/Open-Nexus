"""Embeddings — populate messages.embedding for Layer-3 semantic recall.

Start hosted (quality), measure, then move local (Ollama) if cost or privacy
bites. The dimension must match the schema's vector(N) and EMBEDDING_DIM.
"""

from __future__ import annotations


class Embedder:
    def __init__(self, *, model: str, dim: int) -> None:
        self.model = model
        self.dim = dim

    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector of length ``self.dim``."""
        raise NotImplementedError("Embedder.embed: Phase 1")
