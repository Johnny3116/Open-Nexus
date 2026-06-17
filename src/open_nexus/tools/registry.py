"""ToolRegistry — register tools and run calls through the safety gate.

Every side-effecting tool passes the gate before executing, and every run is
logged as a ``ToolRun`` to the memory store (the audit trail) when a store +
session are supplied. Read-only tools run straight through; gated tools that are
never approved never execute.
"""

from __future__ import annotations

from typing import Any

from open_nexus.contracts.message import Role
from open_nexus.contracts.tool import ApprovalRequest, ToolCall, ToolRun, ToolRunStatus
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

    async def run(
        self,
        call: ToolCall,
        *,
        trace: Trace | None = None,
        store: Any = None,
        session_id: str | None = None,
    ) -> Any:
        """Resolve → gate → execute. Side-effecting tools must pass the gate.

        If ``store`` and ``session_id`` are given, a ``ToolRun`` is persisted via
        ``store.append_message`` (role=tool) for the audit trail.
        """
        trace_id = trace.trace_id if trace else None
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
                self._log(
                    store, session_id, tool, ToolRunStatus.DENIED, call, "denied by gate", trace_id
                )
                return {"error": "denied by approval gate", "tool": tool.name}

        try:
            result = await tool.handler(**call.arguments)
        except Exception as exc:  # noqa: BLE001 - record then re-raise
            self._log(store, session_id, tool, ToolRunStatus.ERROR, call, str(exc), trace_id)
            raise
        if trace:
            trace.emit(Event.TOOL_COMPLETED, tool=tool.name)
        self._log(store, session_id, tool, ToolRunStatus.OK, call, str(result), trace_id)
        return result

    @staticmethod
    def _log(store, session_id, tool, status, call, summary, trace_id) -> None:
        if store is None or session_id is None:
            return
        run = ToolRun(
            tool_name=tool.name,
            arguments=call.arguments,
            status=status,
            risk_level=tool.manifest.risk_level,
            summary=summary[:500],
            trace_id=trace_id,
        )
        store.append_message(
            session_id=session_id,
            role=Role.TOOL,
            content=run.model_dump_json(),
            tool_name=tool.name,
        )
