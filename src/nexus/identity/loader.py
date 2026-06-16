"""Load the identity Markdown files from the identity/ directory."""

from __future__ import annotations

from pathlib import Path


class Identity:
    """Reads SOUL.md / USER.md / TOOLS.md / HEARTBEAT.md from disk."""

    def __init__(self, identity_dir: str | Path = "identity") -> None:
        self.dir = Path(identity_dir)

    def _read(self, name: str) -> str:
        path = self.dir / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def soul(self) -> str:
        """Slot #1 of the system prompt — the global personality."""
        return self._read("SOUL.md")

    def user(self) -> str:
        return self._read("USER.md")

    def tools(self) -> str:
        return self._read("TOOLS.md")

    def heartbeat(self) -> str:
        return self._read("HEARTBEAT.md")

    def user_and_tools(self) -> str:
        """Slot #2 — profile + tool conventions, concatenated."""
        return f"{self.user()}\n\n{self.tools()}".strip()
