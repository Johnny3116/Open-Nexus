"""Streaming contract over the in-process providers."""

from __future__ import annotations

from open_nexus.contracts.message import Message, Role
from open_nexus.contracts.provider import ProviderResponse
from open_nexus.providers.fake import EchoProvider, FakeProvider

MESSAGES = [Message(role=Role.USER, content="hello there")]


async def _collect(stream) -> str:
    return "".join([chunk async for chunk in stream])


async def test_echo_streams_chunks():
    chunks = [c async for c in EchoProvider().stream(system="s", messages=MESSAGES)]
    assert len(chunks) > 1
    assert "".join(chunks).strip() == "echo: hello there"


async def test_fake_stream_matches_complete():
    provider = FakeProvider([ProviderResponse(text="one two three")])
    streamed = await _collect(provider.stream(system="s", messages=MESSAGES))
    assert streamed.strip() == "one two three"
