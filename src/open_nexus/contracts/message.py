"""The internal message format — vendor-agnostic."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """One message in a conversation, independent of any provider."""

    role: Role
    content: str
    # Set when role == TOOL: which tool produced this result.
    tool_name: str | None = None
