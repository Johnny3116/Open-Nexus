"""Context assembly — identity (slot #1) + memory, built each turn.

The system prompt is assembled here, from files you own, so swapping the model
never changes who Nexus is. Phase 0: SOUL/USER/TOOLS + recent history. Layered
retrieval (FTS + vectors) slots in at ``# retrieval`` in a later phase.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from open_nexus.contracts.message import Message, Role
from open_nexus.memory.base import MemoryStore


class AssembledContext(BaseModel):
    system: str
    messages: list[Message]


class ContextAssembler:
    def __init__(self, *, identity_dir: str | Path = "identity", history_limit: int = 20) -> None:
        self.identity_dir = Path(identity_dir)
        self.history_limit = history_limit

    def _read(self, name: str) -> str:
        path = self.identity_dir / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _system_prompt(self) -> str:
        # Slot #1: SOUL (global personality). Then USER + TOOLS conventions.
        parts = [self._read("SOUL.md"), self._read("USER.md"), self._read("TOOLS.md")]
        return "\n\n".join(p for p in parts if p).strip()

    def assemble(self, *, session_id: str, store: MemoryStore, user_text: str) -> AssembledContext:
        history = store.recent(session_id=session_id, limit=self.history_limit)
        # retrieval: + Layer-1 core memory + FTS/vector recall (later phase)
        messages = [*history, Message(role=Role.USER, content=user_text)]
        return AssembledContext(system=self._system_prompt(), messages=messages)
