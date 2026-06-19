"""ApprovalManager — the pending-approval lifecycle.

When a gated tool call needs a human yes, the gate suspends on
``ApprovalManager.confirm``: the request is registered as *pending* and the call
awaits a decision. An out-of-band ``approve(id)`` / ``reject(id)`` (e.g. from the
API endpoints) resolves it. This is what lets "POST /v1/tools/approve" unblock a
tool the model wants to run, while a tool that is never approved simply never
executes.
"""

from __future__ import annotations

import asyncio

from open_nexus.contracts.tool import ApprovalRequest


class ApprovalManager:
    """Tracks pending approvals and resolves them by id."""

    def __init__(self) -> None:
        # id -> (request, future-awaiting-the-decision)
        self._pending: dict[str, tuple[ApprovalRequest, asyncio.Future[bool]]] = {}

    def pending(self) -> list[ApprovalRequest]:
        return [req for req, _ in self._pending.values()]

    async def confirm(self, request: ApprovalRequest) -> bool:
        """Register the request as pending and await an approve/reject decision.

        Suitable as an ``ApprovalGate`` confirmer. The future is created on the
        running loop, so resolve it from the same loop.
        """
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[bool] = loop.create_future()
        self._pending[request.id] = (request, fut)
        try:
            return await fut
        finally:
            self._pending.pop(request.id, None)

    def approve(self, approval_id: str) -> bool:
        """Approve a pending request. Returns False if the id is unknown."""
        return self._resolve(approval_id, True)

    def reject(self, approval_id: str) -> bool:
        """Reject a pending request. Returns False if the id is unknown."""
        return self._resolve(approval_id, False)

    def _resolve(self, approval_id: str, decision: bool) -> bool:
        entry = self._pending.get(approval_id)
        if entry is None:
            return False
        _, fut = entry
        if not fut.done():
            fut.set_result(decision)
        return True
