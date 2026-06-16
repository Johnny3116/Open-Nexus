"""Tool — a manifest paired with an async handler."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from open_nexus.contracts.tool import ToolManifest

ToolHandler = Callable[..., Awaitable[Any]]


@dataclass
class Tool:
    manifest: ToolManifest
    handler: ToolHandler

    @property
    def name(self) -> str:
        return self.manifest.name
