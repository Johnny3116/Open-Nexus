"""Layered memory, Hermes-style, backed by Supabase (Postgres + pgvector + FTS).

    Layer 1 — Core (frozen per session): small curated nexus_memory + user_profile,
              loaded at session start, hard token cap (~1-2k). On a memory flush
              before compaction, durable facts are extracted and written here.
    Layer 2 — Conversation history (unbounded, searchable): every turn stored;
              retrieved on demand via FTS + vector similarity, then summarised
              back into the loop.
    Layer 3 — Semantic / long-term: embeddings over messages + extracted facts.
    Layer 4 — Skills (procedural): later.

SECURITY: all access goes through Core with the service-role key, server-side.
No client (widget, web UI, channel adapter) ever talks to Supabase directly.
"""

from nexus.memory.store import MemoryStore

__all__ = ["MemoryStore"]
