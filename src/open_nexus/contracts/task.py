"""TaskPacket — the delegation contract (Nexus → Jarvis).

A well-formed coding task handed from the conversational agent to the delegated
coding agent (Claude Code / Jarvis). Kept as a contract so delegation,
verification, and reporting all speak the same shape. Fleshed out in the
delegation phase; defined here so the boundary is visible early.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class TaskPacket(BaseModel):
    """A unit of delegated work with everything Jarvis needs to act."""

    title: str
    brief: str  # what to build/fix, in detail
    context: str = ""  # relevant background
    acceptance: list[str] = Field(default_factory=list)  # how we know it's done
    status: TaskStatus = TaskStatus.SUBMITTED
    trace_id: str | None = None
