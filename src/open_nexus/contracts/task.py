"""TaskPacket — the delegation contract (Nexus → Jarvis).

A well-formed coding task handed from the conversational agent to the delegated
coding agent (Claude Code / Jarvis). Kept as a contract so delegation,
verification, and reporting all speak the same shape: Nexus stays light and hands
build/fix/refactor work to Jarvis with everything needed to act *and* to check
the work afterwards.
"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class VerificationStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class VerificationStep(BaseModel):
    """One check that proves the delegated work is actually done.

    "Remember methods, not just facts": a packet carries *how to verify*, not just
    what to build, so the handoff is closeable rather than vibes-based.
    """

    description: str
    command: str | None = None  # optional command to run (e.g. "uv run pytest")
    expected: str | None = None  # the signal that means success
    status: VerificationStatus = VerificationStatus.PENDING


class TaskPacket(BaseModel):
    """A unit of delegated work with everything Jarvis needs to act + verify."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    title: str
    brief: str  # what to build/fix, in detail
    context: str = ""  # relevant background
    acceptance: list[str] = Field(default_factory=list)  # human-readable "done"
    verification: list[VerificationStep] = Field(default_factory=list)  # structured checks
    status: TaskStatus = TaskStatus.SUBMITTED
    trace_id: str | None = None


@runtime_checkable
class Delegate(Protocol):
    """A target that can take a TaskPacket and act on it (e.g. Jarvis).

    Implementations must *fail closed*: if they are not configured/enabled, they
    raise rather than silently pretending the work was handed off.
    """

    async def delegate(self, packet: TaskPacket) -> TaskPacket:
        """Hand off the packet; return it with an updated status."""
        ...
