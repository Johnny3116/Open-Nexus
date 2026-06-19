"""Approval API surface: pending listing + approve/reject wiring."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from open_nexus.api.server import build_app
from open_nexus.gateway.router import Gateway
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.providers.fake import EchoProvider
from open_nexus.safety.approval_manager import ApprovalManager


@pytest.fixture
def client() -> TestClient:
    gateway = Gateway(
        provider=EchoProvider(),
        store=SQLiteStore(":memory:"),
        approvals=ApprovalManager(),
        active_model="echo",
    )
    return TestClient(build_app(gateway))


def test_pending_starts_empty(client):
    assert client.get("/v1/tools/pending").json() == {"pending": []}


def test_approve_unknown_id_404(client):
    assert client.post("/v1/tools/approve", json={"id": "nope"}).status_code == 404


def test_reject_unknown_id_404(client):
    assert client.post("/v1/tools/reject", json={"id": "nope"}).status_code == 404


def test_endpoints_404_when_approvals_disabled():
    gateway = Gateway(provider=EchoProvider(), store=SQLiteStore(":memory:"), active_model="echo")
    c = TestClient(build_app(gateway))
    assert c.get("/v1/tools/pending").status_code == 404
    assert c.post("/v1/tools/approve", json={"id": "x"}).status_code == 404
