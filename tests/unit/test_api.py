"""HTTP API — exercised with FastAPI's TestClient (no network).

Reuses the same Gateway as the channel loop, so this also proves the shared
authorise → resolve → run-loop path.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from open_nexus.api.server import build_app
from open_nexus.gateway.auth import Allowlist
from open_nexus.gateway.router import Gateway
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.providers.fake import EchoProvider


@pytest.fixture
def client() -> TestClient:
    allow = Allowlist()
    allow.allow("web", "alice")
    gateway = Gateway(
        provider=EchoProvider(),
        store=SQLiteStore(":memory:"),
        allowlist=allow,
        active_model="echo",
    )
    return TestClient(build_app(gateway))


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_post_message_round_trip(client):
    resp = client.post(
        "/v1/messages",
        json={"channel": "web", "channel_user_id": "alice", "text": "hello"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "echo: hello"
    assert body["session_id"] == "web:alice"


def test_session_history_after_message(client):
    client.post(
        "/v1/messages",
        json={"channel": "web", "channel_user_id": "alice", "text": "remember this"},
    )
    history = client.get("/v1/sessions/web:alice").json()["messages"]
    assert [(m["role"], m["content"]) for m in history] == [
        ("user", "remember this"),
        ("assistant", "echo: remember this"),
    ]


def test_unauthorised_user_gets_403(client):
    resp = client.post(
        "/v1/messages",
        json={"channel": "web", "channel_user_id": "intruder", "text": "hi"},
    )
    assert resp.status_code == 403
