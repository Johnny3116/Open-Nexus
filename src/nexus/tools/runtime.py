"""Tool runtime — execute a model's tool call, through the approval gate."""

from __future__ import annotations

from typing import Any


class ToolRuntime:
    def __init__(self, *, registry, approval_gate) -> None:
        self.registry = registry
        self.approval_gate = approval_gate

    async def run(self, call) -> Any:
        """Execute one ToolCall: resolve -> (maybe) approve -> run -> result."""
        tool = self.registry.get(call.name)
        if tool is None:
            return {"error": f"unknown tool: {call.name}"}

        if self.approval_gate.requires_approval(tool):
            from nexus.tools.approval import ApprovalRequest

            request = ApprovalRequest(
                tool_name=tool.name,
                summary=f"{tool.name}({call.arguments})",
                arguments=call.arguments,
            )
            if not await self.approval_gate.confirm(request):
                return {"error": "denied by approval gate"}

        return await tool.handler(**call.arguments)
