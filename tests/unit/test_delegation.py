"""Delegation: packet formatting, fail-closed handoff, and gated tool."""

from __future__ import annotations

import pytest

from open_nexus.contracts.task import TaskPacket, TaskStatus, VerificationStep
from open_nexus.contracts.tool import RiskLevel, ToolCall
from open_nexus.delegation.jarvis import DelegationNotConfigured, JarvisDelegate
from open_nexus.delegation.tool import delegate_tool
from open_nexus.safety.approval import ApprovalGate
from open_nexus.tools.registry import ToolRegistry


def _packet() -> TaskPacket:
    return TaskPacket(
        title="Add a /metrics endpoint",
        brief="Expose Prometheus metrics on the API.",
        context="FastAPI app in api/server.py",
        acceptance=["GET /metrics returns 200"],
        verification=[VerificationStep(description="run the API tests", command="uv run pytest")],
    )


# --- packet formatting ------------------------------------------------------


def test_format_handoff_includes_all_sections():
    brief = JarvisDelegate().format_handoff(_packet())
    assert "# Task: Add a /metrics endpoint" in brief
    assert "## Context" in brief
    assert "## Acceptance" in brief
    assert "- GET /metrics returns 200" in brief
    assert "## Verification" in brief
    assert "uv run pytest" in brief


# --- fail-closed handoff ----------------------------------------------------


async def test_delegate_fails_closed_when_disabled():
    with pytest.raises(DelegationNotConfigured):
        await JarvisDelegate().delegate(_packet())


async def test_delegate_fails_closed_without_endpoint():
    with pytest.raises(DelegationNotConfigured):
        await JarvisDelegate(enabled=True).delegate(_packet())


async def test_delegate_submits_when_configured():
    delegate = JarvisDelegate(endpoint="http://jarvis.local", enabled=True)
    result = await delegate.delegate(_packet())
    assert result.status == TaskStatus.SUBMITTED


# --- delegate_to_jarvis tool: gated EXTERNAL, fail-closed at the gate -------


def test_delegate_tool_is_gated_external():
    tool = delegate_tool(JarvisDelegate())
    assert tool.manifest.risk_level == RiskLevel.EXTERNAL
    assert tool.manifest.requires_approval is True


async def test_delegate_tool_denied_without_approval():
    reg = ToolRegistry()  # default gate denies gated actions
    reg.register(delegate_tool(JarvisDelegate(endpoint="x", enabled=True)))
    result = await reg.run(
        ToolCall(id="1", name="delegate_to_jarvis", arguments={"title": "t", "brief": "b"})
    )
    assert result == {"error": "denied by approval gate", "tool": "delegate_to_jarvis"}


async def test_delegate_tool_runs_when_approved():
    # Auto-approve, configured delegate → handoff goes through.
    async def approve(_req):
        return True

    reg = ToolRegistry(gate=ApprovalGate(confirmer=approve))
    reg.register(delegate_tool(JarvisDelegate(endpoint="x", enabled=True)))
    result = await reg.run(
        ToolCall(id="1", name="delegate_to_jarvis", arguments={"title": "t", "brief": "b"})
    )
    assert result["status"] == "submitted"


async def test_delegate_tool_approved_but_unconfigured_still_fails_closed():
    # Even past the gate, an unconfigured delegate refuses (second fail-closed
    # layer). The registry contains the exception and returns it as an error
    # result so the turn/channel survives — the handoff still did not happen.
    async def approve(_req):
        return True

    reg = ToolRegistry(gate=ApprovalGate(confirmer=approve))
    reg.register(delegate_tool(JarvisDelegate()))  # disabled
    result = await reg.run(
        ToolCall(id="1", name="delegate_to_jarvis", arguments={"title": "t", "brief": "b"})
    )
    assert result["tool"] == "delegate_to_jarvis"
    assert "not enabled" in result["error"]
