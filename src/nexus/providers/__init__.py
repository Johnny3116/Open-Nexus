"""Provider abstraction — "plug any API or subscription in."

One internal message format; adapters translate to/from each provider's API.
Every provider is treated as an OpenAI-compatible-or-translated endpoint, so
cloud and local look identical to the Core. Config-driven model selection with a
fallback chain + exponential backoff so a provider outage degrades, not dies.
"""

from nexus.providers.base import Provider, ProviderResponse, ToolCall

__all__ = ["Provider", "ProviderResponse", "ToolCall"]
