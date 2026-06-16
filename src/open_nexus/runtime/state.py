"""The RuntimeState carried through a single turn."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from open_nexus.contracts.tool import ApprovalRequest, ToolCall


def _new_trace_id() -> str:
    return uuid.uuid4().hex


class RuntimeState(BaseModel):
    """Everything the harness needs to know about the turn in flight.

    Created by the gateway when a message is resolved, then threaded through the
    core loop, providers, tools, and safety. The ``trace_id`` ties every
    observability event for the turn together.
    """

    session_id: str
    user_id: str
    active_model: str
    active_channel: str
    selected_skills: list[str] = Field(default_factory=list)
    pending_tool_calls: list[ToolCall] = Field(default_factory=list)
    pending_approvals: list[ApprovalRequest] = Field(default_factory=list)
    trace_id: str = Field(default_factory=_new_trace_id)
