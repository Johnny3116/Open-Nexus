"""ToolRegistry — register tools and run calls through the safety gate."""

from __future__ import annotations

from typing import Any

from open_nexus.contracts.tool import ApprovalRequest, ToolCall
from open_nexus.observability.events import Event
from open_nexus.observability.trace import Trace
from open_nexus.safety.approval import ApprovalGate
from open_nexus.tools.base import Tool


class ToolRegistry:
    def __init__(self, *, gate: ApprovalGate | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        self._gate = gate or ApprovalGate()

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def specs(self) -> list[dict]:
        """Provider-agnostic tool specs for the model request."""
        return [
            {
                "name": t.manifest.name,
                "description": t.manifest.description,
                "parameters": t.manifest.parameters,
            }
            for t in self._tools.values()
        ]

    async def run(self, call: ToolCall, *, trace: Trace | None = None) -> Any:
        """Resolve → gate → execute. Side-effecting tools must pass the gate."""
        tool = self._tools.get(call.name)
        if tool is None:
            return {"error": f"unknown tool: {call.name}"}

        request = ApprovalRequest(
            tool_name=tool.name,
            risk_level=tool.manifest.risk_level,
            summary=f"{tool.name}({call.arguments})",
            arguments=call.arguments,
        )
        if self._gate.requires_approval(tool.manifest):
            if trace:
                trace.emit(Event.APPROVAL_REQUIRED, tool=tool.name, risk=tool.manifest.risk_level)
            approved = await self._gate.review(tool.manifest, request)
            if trace:
                trace.emit(
                    Event.APPROVAL_GRANTED if approved else Event.APPROVAL_DENIED, tool=tool.name
                )
            if not approved:
                return {"error": "denied by approval gate", "tool": tool.name}

        result = await tool.handler(**call.arguments)
        if trace:
            trace.emit(Event.TOOL_COMPLETED, tool=tool.name)
        return result
