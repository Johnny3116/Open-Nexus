"""The approval gate.

Irreversible or external actions require an explicit human "yes" before they run.
The set of gated action types is config-driven (config: [tools].approval_required)
and also flagged per-tool (Tool.requires_approval).

This is non-negotiable given Nexus's tool surface (remote control + screen +
voice + autonomous heartbeat + shell-capable skills). See docs/SECURITY.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    """A pending action awaiting human confirmation."""

    tool_name: str
    summary: str          # one-line, human-readable: what will happen
    arguments: dict


class ApprovalGate:
    """Decides whether a tool call may proceed, prompting the human if needed."""

    def __init__(self, *, gated_actions: set[str], prompt) -> None:
        # `prompt` is an async callable that asks the human and returns a bool.
        self._gated = gated_actions
        self._prompt = prompt

    def requires_approval(self, tool) -> bool:
        return tool.requires_approval or tool.name in self._gated

    async def confirm(self, request: ApprovalRequest) -> bool:
        """Ask the human. Deny by default if no confirmation is obtained."""
        # TODO(phase-2): route the prompt to the originating channel and await
        # an explicit yes. A heartbeat must never auto-approve a paid action.
        return await self._prompt(request)
