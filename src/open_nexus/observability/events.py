"""The canonical lifecycle event vocabulary.

Emit these (not free-form strings) so traces are queryable and stable.
"""

from __future__ import annotations

from enum import StrEnum


class Event(StrEnum):
    MESSAGE_RECEIVED = "message.received"
    CONTEXT_BUILT = "context.built"
    PROVIDER_SELECTED = "provider.selected"
    PROVIDER_COMPLETED = "provider.completed"
    TOOL_REQUESTED = "tool.requested"
    APPROVAL_REQUIRED = "approval.required"
    APPROVAL_GRANTED = "approval.granted"
    APPROVAL_DENIED = "approval.denied"
    TOOL_COMPLETED = "tool.completed"
    MEMORY_WRITTEN = "memory.written"
    RESPONSE_SENT = "response.sent"
    ERROR = "error"
