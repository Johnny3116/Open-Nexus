"""Gateway router — drives a channel's stream through the full pipeline.

This is the orchestrator: for each inbound message it authorises, resolves the
session, runs the core loop under the per-session lock, and serialises the reply
back out. It is the one place that knows about both channels and the core.
"""

from __future__ import annotations

from open_nexus.contracts.channel import Channel
from open_nexus.core.context import ContextAssembler
from open_nexus.core.loop import run_turn
from open_nexus.core.session import SessionRegistry
from open_nexus.gateway.auth import Allowlist
from open_nexus.gateway.inbound import Rejected, resolve_inbound
from open_nexus.gateway.outbound import send_reply
from open_nexus.gateway.rate_limit import TokenBucket
from open_nexus.observability.logger import get_logger
from open_nexus.observability.trace import Trace

_log = get_logger("open_nexus.gateway")


class Gateway:
    def __init__(
        self,
        *,
        provider,
        store,
        assembler: ContextAssembler | None = None,
        allowlist: Allowlist | None = None,
        sessions: SessionRegistry | None = None,
        active_model: str = "echo",
        rate_limiter: TokenBucket | None = None,
    ) -> None:
        self.provider = provider
        self.store = store
        self.assembler = assembler or ContextAssembler()
        self.allowlist = allowlist or Allowlist()
        self.sessions = sessions or SessionRegistry()
        self.active_model = active_model
        self.rate_limiter = rate_limiter or TokenBucket()

    async def run(self, channel: Channel) -> None:
        """Serve one channel until its stream ends."""
        async for msg in channel.listen():
            try:
                state = resolve_inbound(
                    msg,
                    allowlist=self.allowlist,
                    sessions=self.sessions,
                    active_model=self.active_model,
                )
            except Rejected as exc:
                _log.warning("rejected inbound: %s", exc)
                continue

            if not self.rate_limiter.allow(state.user_id):
                await send_reply(
                    channel, channel_user_id=msg.channel_user_id, text="Slow down a moment."
                )
                continue

            # Serialise turns per session: a message arriving mid-run waits its turn.
            async with self.sessions.lock_for(state.session_id):
                reply = await run_turn(
                    user_text=msg.text,
                    state=state,
                    provider=self.provider,
                    assembler=self.assembler,
                    store=self.store,
                    trace=Trace(state.trace_id),
                )
            await send_reply(channel, channel_user_id=msg.channel_user_id, text=reply)
