"""FastAPI server — the shared runtime API (Phase 2).

One runtime, many front ends: the desktop GUI, a Discord bot, a voice client, a
mobile monitor, and Jarvis all talk to the same Core over this API rather than
each re-implementing the loop. Requires the ``web`` extra (fastapi/uvicorn).

    POST /v1/messages          # send a message, get a reply
    GET  /v1/sessions/{id}     # session history
    GET  /health
    # later: POST /v1/tools/approve, GET /v1/events/stream, WebSocket /v1/ws

The app reuses ``Gateway.handle`` so there is exactly one authorise → resolve →
run-loop path across channels and HTTP.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from open_nexus.contracts.channel import InboundMessage
from open_nexus.gateway.inbound import Rejected
from open_nexus.gateway.rate_limit import RateLimited
from open_nexus.gateway.router import Gateway


# Request/response models live at module scope so FastAPI can resolve the
# annotations (with `from __future__ import annotations` a model defined inside
# build_app would be unresolvable and treated as a query param).
class MessageIn(BaseModel):
    channel: str
    channel_user_id: str
    text: str


class MessageOut(BaseModel):
    reply: str
    session_id: str


def build_app(gateway: Gateway) -> Any:
    """Return a FastAPI app exposing the v1 API over the given Gateway."""
    from fastapi import FastAPI, HTTPException

    app = FastAPI(title="Open-Nexus", version="0.0.1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/messages", response_model=MessageOut)
    async def post_message(body: MessageIn) -> MessageOut:
        msg = InboundMessage(
            channel=body.channel, channel_user_id=body.channel_user_id, text=body.text
        )
        try:
            reply, session_id = await gateway.handle(msg)
        except Rejected as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except RateLimited as exc:
            raise HTTPException(status_code=429, detail="rate limited") from exc
        return MessageOut(reply=reply, session_id=session_id)

    @app.get("/v1/sessions/{session_id}")
    async def get_session(session_id: str, limit: int = 50) -> dict[str, Any]:
        history = gateway.store.recent(session_id=session_id, limit=limit)
        return {
            "session_id": session_id,
            "messages": [
                {"role": m.role.value, "content": m.content, "tool_name": m.tool_name}
                for m in history
            ],
        }

    return app
