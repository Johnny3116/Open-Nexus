"""Tool registry — the authoritative list of callable tools.

The natural-language guidance for these lives in identity/TOOLS.md; the
machine-readable definitions live here.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    """A callable capability exposed to the model."""

    name: str
    description: str
    parameters: dict[str, Any]            # JSON-schema-ish parameter spec
    handler: Callable[..., Awaitable[Any]]
    requires_approval: bool = False        # set for irreversible/external actions


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def specs(self) -> list[dict]:
        """Provider-agnostic tool specs for the model request."""
        return [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in self._tools.values()
        ]
