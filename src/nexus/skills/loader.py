"""SKILL.md loader — parse frontmatter, index, and load on demand."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Skill:
    """A parsed SKILL.md: frontmatter metadata + the instruction body."""

    name: str
    description: str
    path: Path
    triggers: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    trust: str = "untrusted"  # 'builtin' | 'reviewed' | 'untrusted'
    body: str = ""


class SkillLoader:
    """Discovers SKILL.md files and loads the relevant ones per turn."""

    def __init__(self, skills_dir: str | Path = "skills") -> None:
        self.dir = Path(skills_dir)

    def discover(self) -> list[Path]:
        """Find all SKILL.md files under the skills directory."""
        return sorted(self.dir.glob("*/SKILL.md"))

    def load(self, path: Path) -> Skill:
        # TODO(phase-2): parse YAML frontmatter + body into a Skill.
        raise NotImplementedError("SkillLoader.load: Phase 2")

    def relevant(self, query: str) -> list[Skill]:
        """Return skills whose triggers match the query (loaded on demand)."""
        # TODO(phase-2): match triggers/description against the query.
        raise NotImplementedError("SkillLoader.relevant: Phase 2")
