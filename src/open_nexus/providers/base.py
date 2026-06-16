"""Shared adapter helpers.

The ``Provider`` *protocol* lives in ``open_nexus.contracts.provider`` — providers
adapt to it, they don't own it. This module holds small helpers shared by real
adapters (role mapping, etc.) so each vendor file stays focused on its API.
"""

from __future__ import annotations

from open_nexus.contracts.message import Message

# Most chat APIs only accept user/assistant turns; tool results fold into a user
# turn. Adapters that support native tool roles can override this.
_DEFAULT_ROLE_MAP = {"system": "system", "user": "user", "assistant": "assistant", "tool": "user"}


def to_chat_messages(messages: list[Message], role_map: dict[str, str] | None = None) -> list[dict]:
    """Map internal Messages to the common ``{role, content}`` chat shape."""
    rm = role_map or _DEFAULT_ROLE_MAP
    return [{"role": rm.get(m.role.value, "user"), "content": m.content} for m in messages]
