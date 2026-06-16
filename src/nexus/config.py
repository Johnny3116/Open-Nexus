"""Configuration loading.

Reads config/nexus.toml (TOML) and resolves ``*_env`` keys against the
environment (.env loaded via python-dotenv). Secrets never live in the TOML;
only the *name* of the env var that holds them does.

Phase 0: minimal loader. Flesh out validation with pydantic models as the
surface grows.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:  # py311+ has tomllib in stdlib
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

DEFAULT_CONFIG_PATH = Path("config/nexus.toml")


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load and parse the Nexus TOML config.

    Raises FileNotFoundError with a helpful hint if the user hasn't copied the
    example yet.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"No config at {path}. Copy config/nexus.example.toml to {path} and edit it."
        )
    with path.open("rb") as fh:
        return tomllib.load(fh)


def resolve_env(name: str) -> str | None:
    """Look up a secret from the environment by var name (never logged)."""
    return os.environ.get(name)


# TODO(phase-1): typed Config model (pydantic), env-var resolution for `*_env`
# keys, and validation that the active provider has its key present.
