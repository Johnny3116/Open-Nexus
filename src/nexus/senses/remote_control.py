"""Remote computer control — keyboard / mouse / window automation.

THE SINGLE MOST DANGEROUS CAPABILITY IN THE SYSTEM. Defaults to
*suggest-and-confirm*, never autonomous action. Every action passes through the
approval gate. Scoped to one machine, opt-in per session, never silent. Built
last, behind the hardest gates. Requires the `control` extra.
"""

from __future__ import annotations


class RemoteControl:
    """Every method here is a gated, irreversible action."""

    def __init__(self, *, approval_gate, enabled: bool = False) -> None:
        self.approval_gate = approval_gate
        self._enabled = enabled

    async def click(self, x: int, y: int) -> None:
        raise NotImplementedError("RemoteControl.click: Phase 3 (gated)")

    async def type_text(self, text: str) -> None:
        raise NotImplementedError("RemoteControl.type_text: Phase 3 (gated)")
