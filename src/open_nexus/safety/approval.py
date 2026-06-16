"""ApprovalGate — ask the human before an irreversible/external action runs."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from open_nexus.contracts.tool import ApprovalRequest, ToolManifest
from open_nexus.safety.policy import SafetyPolicy

# An async callable that surfaces the request to a human and returns their answer.
Confirmer = Callable[[ApprovalRequest], Awaitable[bool]]


async def _deny_by_default(_: ApprovalRequest) -> bool:
    """Fail closed: if no confirmer is wired, gated actions are denied."""
    return False


class ApprovalGate:
    def __init__(self, *, policy: SafetyPolicy | None = None, confirmer: Confirmer | None = None):
        self.policy = policy or SafetyPolicy()
        self._confirm = confirmer or _deny_by_default

    def requires_approval(self, manifest: ToolManifest) -> bool:
        return self.policy.requires_approval(manifest)

    async def review(self, manifest: ToolManifest, request: ApprovalRequest) -> bool:
        """Return True iff the action may proceed.

        Read-only actions pass straight through. Everything gated must get an
        explicit human yes; absent a confirmer, it is denied.
        """
        if not self.requires_approval(manifest):
            return True
        return await self._confirm(request)
