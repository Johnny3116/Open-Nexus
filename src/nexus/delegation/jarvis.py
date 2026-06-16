"""delegate_to_jarvis — the coding hand-off tool."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DelegationResult:
    status: str            # 'submitted' | 'in_progress' | 'done' | 'failed'
    summary: str
    detail: str = ""


class JarvisDelegate:
    def __init__(self, *, endpoint: str) -> None:
        self.endpoint = endpoint

    async def delegate(self, *, task: str, context: str = "") -> DelegationResult:
        """Hand a well-formed coding task to Jarvis and track it.

        Nexus composes the brief, submits it, monitors progress, and reports back
        in its own voice. This module is the transport; the "in its own voice"
        framing happens in the agent loop.
        """
        # TODO(phase-2): submit to the Jarvis endpoint, poll/stream status.
        raise NotImplementedError("JarvisDelegate.delegate: Phase 2")
