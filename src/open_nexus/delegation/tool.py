"""delegate_to_jarvis as a Tool — gated EXTERNAL, so handoff passes the gate.

Two fail-closed layers stack here: the approval gate (an external action needs a
human yes) and the delegate itself (raises if Jarvis isn't configured).
"""

from __future__ import annotations

from open_nexus.contracts.task import Delegate, TaskPacket
from open_nexus.contracts.tool import RiskLevel, ToolManifest
from open_nexus.tools.base import Tool


def delegate_tool(delegate: Delegate) -> Tool:
    async def handler(
        *, title: str, brief: str, context: str = "", acceptance: list[str] | None = None
    ) -> dict[str, str]:
        packet = TaskPacket(title=title, brief=brief, context=context, acceptance=acceptance or [])
        result = await delegate.delegate(packet)
        return {"id": result.id, "status": result.status.value}

    return Tool(
        manifest=ToolManifest(
            name="delegate_to_jarvis",
            description="Hand a build/fix/refactor task to Jarvis.",
            risk_level=RiskLevel.EXTERNAL,
            requires_approval=True,
            parameters={"title": "str", "brief": "str", "context": "str", "acceptance": "list"},
        ),
        handler=handler,
    )
