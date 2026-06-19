"""JarvisDelegate — format a TaskPacket and hand it to Jarvis (stub).

``format_handoff`` builds the human/agent-readable brief (pure, always available).
``delegate`` is the handoff itself: a stub that, for now, marks the packet
SUBMITTED. It **fails closed** — if delegation isn't enabled/configured it raises
``DelegationNotConfigured`` instead of pretending the work was handed off. The
real network call (POST the brief, monitor, report back) is a later step.
"""

from __future__ import annotations

from open_nexus.contracts.task import TaskPacket, TaskStatus


class DelegationNotConfigured(Exception):
    """Raised when delegation is attempted but Jarvis isn't enabled/configured."""


class JarvisDelegate:
    def __init__(self, *, endpoint: str | None = None, enabled: bool = False) -> None:
        self.endpoint = endpoint
        self.enabled = enabled

    def format_handoff(self, packet: TaskPacket) -> str:
        """Render a well-formed brief Jarvis can act on. Pure; no side effects."""
        lines = [f"# Task: {packet.title}", "", packet.brief.strip()]
        if packet.context:
            lines += ["", "## Context", packet.context.strip()]
        if packet.acceptance:
            lines += ["", "## Acceptance", *(f"- {a}" for a in packet.acceptance)]
        if packet.verification:
            lines += ["", "## Verification"]
            for step in packet.verification:
                suffix = f" (`{step.command}`)" if step.command else ""
                lines.append(f"- {step.description}{suffix}")
        return "\n".join(lines)

    async def delegate(self, packet: TaskPacket) -> TaskPacket:
        """Hand the packet to Jarvis. Fails closed when not configured."""
        if not self.enabled or not self.endpoint:
            raise DelegationNotConfigured(
                "Jarvis delegation is not enabled/configured; refusing to hand off"
            )
        # TODO(later): POST format_handoff(packet) to the endpoint, monitor the
        # run, fold results + verification status back into the packet.
        return packet.model_copy(update={"status": TaskStatus.SUBMITTED})
