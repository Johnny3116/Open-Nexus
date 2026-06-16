"""Live smoke — hits a real provider with a tiny prompt. Manual, never in CI.

Run by hand before a release:  uv run pytest tests/live -m live
Skipped automatically without a key. CI runs only tests/unit, so this never fires
there.
"""

from __future__ import annotations

import os

import pytest

from open_nexus.contracts.message import Message, Role

pytestmark = pytest.mark.live


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="needs ANTHROPIC_API_KEY")
async def test_anthropic_live_one_token():
    from open_nexus.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(api_key=os.environ["ANTHROPIC_API_KEY"], model="claude-sonnet-4-6")
    resp = await provider.complete(
        system="Reply with exactly the word: pong",
        messages=[Message(role=Role.USER, content="ping")],
    )
    assert isinstance(resp.text, str) and resp.text
