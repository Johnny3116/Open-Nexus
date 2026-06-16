"""Provider adapters — translate vendor APIs to the harness contracts.

Providers adapt *to* ``open_nexus.contracts.provider``; they do not define it.
Adding a new AI/API = a new adapter + config, never a core-loop change.

Phase 0 ships ``EchoProvider`` / ``FakeProvider`` (no network, no key, no cost) so
the architecture can be proven without provider billing. Real adapters
(Anthropic, OpenAI, local) require their optional extras and are imported lazily.
"""

from open_nexus.providers.fake import EchoProvider, FakeProvider

__all__ = ["EchoProvider", "FakeProvider"]
