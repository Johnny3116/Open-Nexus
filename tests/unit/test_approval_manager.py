"""ApprovalManager lifecycle: a gated call suspends until approve/reject."""

from __future__ import annotations

import asyncio

from open_nexus.contracts.tool import ApprovalRequest, RiskLevel
from open_nexus.safety.approval_manager import ApprovalManager


def _req() -> ApprovalRequest:
    return ApprovalRequest(tool_name="rm", risk_level=RiskLevel.WRITE, summary="rm tmp")


async def _wait_pending(m: ApprovalManager) -> None:
    for _ in range(1000):
        if m.pending():
            return
        await asyncio.sleep(0)
    raise AssertionError("nothing became pending")


async def test_approve_resolves_true():
    m = ApprovalManager()
    req = _req()
    task = asyncio.create_task(m.confirm(req))
    await _wait_pending(m)
    assert [r.id for r in m.pending()] == [req.id]
    assert m.approve(req.id) is True
    assert await task is True
    assert m.pending() == []


async def test_reject_resolves_false():
    m = ApprovalManager()
    req = _req()
    task = asyncio.create_task(m.confirm(req))
    await _wait_pending(m)
    assert m.reject(req.id) is True
    assert await task is False
    assert m.pending() == []


def test_unknown_id_returns_false():
    m = ApprovalManager()
    assert m.approve("nope") is False
    assert m.reject("nope") is False
