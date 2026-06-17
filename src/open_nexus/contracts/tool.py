"""Tool contracts — manifests, calls, and approval requests.

Tools *declare* risk via a ``ToolManifest``; the ``safety`` package *enforces* it.
This split (point 10 of the design revision) makes the approval system reusable
across tools, skills, delegation, scheduler jobs, and remote control — none of
them need their own bespoke gate.
"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    """Increasing blast radius. ``safety.policy`` maps these to gate behaviour."""

    READ = "read"  # no side effects
    WRITE = "write"  # local mutation (rename/move files)
    EXTERNAL = "external"  # sends/spends/posts off the box
    SHELL = "shell"  # arbitrary command execution
    CONTROL = "control"  # keyboard/mouse/window automation — the hardest gate


class ToolManifest(BaseModel):
    """What a tool is and how dangerous it is. Declared by the tool."""

    name: str
    description: str = ""
    risk_level: RiskLevel = RiskLevel.READ
    requires_approval: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """A tool invocation requested by the model, normalised."""

    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    """A pending action awaiting explicit human confirmation.

    The ``id`` correlates the suspended tool call with an out-of-band approve /
    reject decision (e.g. the API endpoints), so the gate knows which pending
    action a decision resolves.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    tool_name: str
    risk_level: RiskLevel
    summary: str  # one-line, human-readable: what will happen
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolRunStatus(StrEnum):
    OK = "ok"
    DENIED = "denied"  # blocked by the approval gate
    ERROR = "error"


class ToolRun(BaseModel):
    """A record of one tool execution, logged to memory for the audit trail."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: ToolRunStatus
    risk_level: RiskLevel
    summary: str = ""  # short result/error description
    trace_id: str | None = None
