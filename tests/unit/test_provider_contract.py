"""Provider contract suite — every in-process provider passes the same checks.

This is "adapter tests as contract tests" (design revision point 14) applied to
the providers we can run hermetically. Real-network adapters get their translation
covered in test_adapter_translation.py and a live smoke under the ``live`` marker.
"""

from __future__ import annotations

import pytest

from open_nexus.contracts.message import Message, Role
from open_nexus.contracts.provider import (
    Provider,
    ProviderCapabilities,
    ProviderResponse,
    SupportsStreaming,
)
from open_nexus.providers.fake import EchoProvider, FakeProvider

# Factories, not instances: each test gets a fresh provider so a FakeProvider's
# single-shot script isn't exhausted by an earlier test.
_FACTORIES = {
    "echo": EchoProvider,
    "fake": lambda: FakeProvider([ProviderResponse(text="scripted")]),
}


@pytest.fixture(params=list(_FACTORIES), ids=list(_FACTORIES))
def provider(request):
    return _FACTORIES[request.param]()


def test_satisfies_provider_protocol(provider):
    assert isinstance(provider, Provider)


def test_exposes_capabilities(provider):
    assert isinstance(provider.capabilities, ProviderCapabilities)


async def test_complete_returns_normalised_response(provider):
    resp = await provider.complete(system="s", messages=[Message(role=Role.USER, content="hi")])
    assert isinstance(resp, ProviderResponse)
    assert isinstance(resp.text, str)


async def test_handles_empty_history(provider):
    resp = await provider.complete(system="s", messages=[])
    assert isinstance(resp, ProviderResponse)


def test_streaming_capability_implies_stream_method(provider):
    # If a provider advertises streaming, it must actually implement the contract.
    if provider.capabilities.streaming:
        assert isinstance(provider, SupportsStreaming)
