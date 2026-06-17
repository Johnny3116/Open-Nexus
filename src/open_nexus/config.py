"""Configuration — secrets from env, provider routing from YAML.

Two sources, by design:
  - **Secrets** (API keys, Supabase service-role key) come from the environment
    via pydantic-settings / ``.env``. They are never written to a config file.
  - **Provider routing** (default, fallback chain, per-provider type/model) comes
    from ``config.yaml`` so adding an AI/API is config, not code.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    """Secrets loaded from environment / .env. Never committed."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    local_base_url: str = "http://localhost:11434/v1"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None


class ProviderConfig(BaseModel):
    type: str  # 'fake' | 'anthropic' | 'openai' | 'local'
    model: str | None = None
    base_url: str | None = None


class ProvidersConfig(BaseModel):
    default: str = "echo"
    fallback: list[str] = []
    providers: dict[str, ProviderConfig] = {}


class MemoryConfig(BaseModel):
    backend: str = "sqlite"  # 'sqlite' (Phase 0) | 'supabase' (persistent)
    path: str = "nexus.sqlite"  # SQLite file when backend == 'sqlite'


class Config(BaseModel):
    secrets: Secrets
    routing: ProvidersConfig
    memory: MemoryConfig = MemoryConfig()
    identity_dir: str = "identity"


def load_config(path: str | Path = "config.yaml") -> Config:
    """Load routing + memory YAML (if present) + secrets from env."""
    path = Path(path)
    routing = ProvidersConfig()
    memory = MemoryConfig()
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        routing = ProvidersConfig.model_validate(data)
        if "memory" in data:
            memory = MemoryConfig.model_validate(data["memory"])
    return Config(secrets=Secrets(), routing=routing, memory=memory)
