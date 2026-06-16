"""Inbound pipeline — normalise + authorise + resolve a turn's RuntimeState.

Pure-ish (no model call) so it is cheap to unit-test: given an InboundMessage,
does the gateway admit it, and what RuntimeState does it produce?
"""

from __future__ import annotations

from open_nexus.contracts.channel import InboundMessage
from open_nexus.core.session import SessionRegistry
from open_nexus.gateway.auth import Allowlist
from open_nexus.runtime.state import RuntimeState


class Rejected(Exception):
    """Raised when an inbound message is not authorised."""


def resolve_inbound(
    msg: InboundMessage,
    *,
    allowlist: Allowlist,
    sessions: SessionRegistry,
    active_model: str,
) -> RuntimeState:
    if not allowlist.is_allowed(msg.channel, msg.channel_user_id):
        raise Rejected(f"{msg.channel_user_id} not allowed on {msg.channel}")
    session = sessions.resolve(channel=msg.channel, channel_user_id=msg.channel_user_id)
    return RuntimeState(
        session_id=session.id,
        user_id=session.user_id,
        active_model=active_model,
        active_channel=msg.channel,
    )
