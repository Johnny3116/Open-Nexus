"""Context assembler.

Builds the prompt for each turn from a small, stable set of pieces so model
swapping stays cheap and prompt-caching stays warm:

    slot #1  SOUL.md                       (global personality — always first)
    slot #2  USER.md + TOOLS.md            (your profile + tool conventions)
    slot #3  Layer-1 core memory           (nexus_memory + user_profile, capped)
    slot #4  Layer-2 retrieval             (top-k FTS + top-k vector, deduped,
                                            summarised back into the loop)
    slot #5  current message

Retrieval per turn: Layer 1 (all, capped) + Layer 2 (top-k FTS + top-k vector on
the current query, deduped, summarised) -> assemble -> call model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AssembledContext:
    """The final, ordered message list handed to a provider, plus metadata."""

    system: str
    messages: list[dict]
    token_estimate: int = 0


class ContextAssembler:
    """Pulls identity + memory together into an AssembledContext each turn."""

    def __init__(self, *, identity, memory, core_memory_token_cap: int = 1500) -> None:
        self.identity = identity
        self.memory = memory
        self.core_memory_token_cap = core_memory_token_cap

    def assemble(self, session, message: str) -> AssembledContext:
        # TODO(phase-1):
        #   soul   = self.identity.soul()                  # slot #1
        #   user   = self.identity.user_and_tools()        # slot #2
        #   core   = self.memory.core(session.user_id, cap=self.core_memory_token_cap)
        #   recall = self.memory.retrieve(session, query=message)  # FTS + vector
        #   build system prompt + message list
        raise NotImplementedError("ContextAssembler.assemble: Phase 1")
