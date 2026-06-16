"""Build providers (and the router) from config + secrets.

Keeps the wiring of "config name → concrete adapter" in one place. Real adapters
are imported lazily inside each branch so Phase 0 (echo/fake only) needs none of
the optional SDKs installed.
"""

from __future__ import annotations

from open_nexus.config import Config, ProviderConfig
from open_nexus.contracts.provider import Provider
from open_nexus.providers.fake import EchoProvider
from open_nexus.providers.router import ProviderRouter


def build_provider(name: str, cfg: Config) -> Provider:
    # An unconfigured name (e.g. the Phase-0 "echo" default) gets sensible defaults.
    pc = cfg.routing.providers.get(name) or ProviderConfig(type=name)

    if pc.type in {"echo", "fake"}:
        return EchoProvider()
    if pc.type == "anthropic":
        from open_nexus.providers.anthropic import AnthropicProvider

        return AnthropicProvider(
            api_key=cfg.secrets.anthropic_api_key or "", model=pc.model or "claude-sonnet-4-6"
        )
    if pc.type == "openai":
        from open_nexus.providers.openai import OpenAIProvider

        return OpenAIProvider(
            api_key=cfg.secrets.openai_api_key, model=pc.model or "gpt-4o", base_url=pc.base_url
        )
    if pc.type == "local":
        from open_nexus.providers.local import LocalProvider

        return LocalProvider(
            base_url=pc.base_url or cfg.secrets.local_base_url, model=pc.model or "llama3.1"
        )
    raise ValueError(f"unknown provider type: {pc.type!r}")


def build_router(cfg: Config) -> ProviderRouter:
    """Construct the full router from the routing config (default + fallbacks)."""
    names = {cfg.routing.default, *cfg.routing.fallback}
    providers = {n: build_provider(n, cfg) for n in names}
    return ProviderRouter(
        providers=providers, default=cfg.routing.default, fallback=cfg.routing.fallback
    )
