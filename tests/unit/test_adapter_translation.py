"""Real-adapter translation, network-free.

We inject a fake vendor client and assert the adapter maps the vendor payload to
our ``ProviderResponse`` (text + tool calls). This is what makes "any AI/API"
real without hitting the network or needing keys.
"""

from __future__ import annotations

from types import SimpleNamespace

from open_nexus.contracts.message import Message, Role
from open_nexus.providers.anthropic import AnthropicProvider
from open_nexus.providers.openai import OpenAIProvider

MESSAGES = [Message(role=Role.USER, content="hi")]


# --- Anthropic: content blocks (text + tool_use) → ProviderResponse ---------


class _FakeAnthropicMessages:
    def __init__(self, content):
        self._content = content

    async def create(self, **kwargs):
        return SimpleNamespace(content=self._content)


class _FakeAnthropicClient:
    def __init__(self, content):
        self.messages = _FakeAnthropicMessages(content)


async def test_anthropic_maps_text_and_tool_use():
    content = [
        SimpleNamespace(type="text", text="hello "),
        SimpleNamespace(type="text", text="world"),
        SimpleNamespace(type="tool_use", id="t1", name="clock", input={"tz": "utc"}),
    ]
    provider = AnthropicProvider(api_key="x", model="m", client=_FakeAnthropicClient(content))
    resp = await provider.complete(system="s", messages=MESSAGES)
    assert resp.text == "hello world"
    assert [(c.name, c.arguments) for c in resp.tool_calls] == [("clock", {"tz": "utc"})]


# --- OpenAI: choices[0].message (content + tool_calls) → ProviderResponse ----


class _FakeChatCompletions:
    def __init__(self, message):
        self._message = message

    async def create(self, **kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=self._message)])


class _FakeOpenAIClient:
    def __init__(self, message):
        self.chat = SimpleNamespace(completions=_FakeChatCompletions(message))


async def test_openai_maps_content_and_tool_calls():
    message = SimpleNamespace(
        content="sure",
        tool_calls=[
            SimpleNamespace(
                id="c1", function=SimpleNamespace(name="search", arguments='{"q": "x"}')
            )
        ],
    )
    provider = OpenAIProvider(api_key="x", model="m", client=_FakeOpenAIClient(message))
    resp = await provider.complete(system="s", messages=MESSAGES)
    assert resp.text == "sure"
    assert resp.tool_calls[0].name == "search"
    # arguments are parsed from the JSON string into a real dict, not wrapped
    assert resp.tool_calls[0].arguments == {"q": "x"}


async def test_openai_tolerates_invalid_json_arguments():
    message = SimpleNamespace(
        content="",
        tool_calls=[
            SimpleNamespace(id="c1", function=SimpleNamespace(name="t", arguments="not json"))
        ],
    )
    provider = OpenAIProvider(api_key="x", model="m", client=_FakeOpenAIClient(message))
    resp = await provider.complete(system="s", messages=MESSAGES)
    assert resp.tool_calls[0].arguments == {"raw": "not json"}


async def test_openai_handles_no_tool_calls():
    message = SimpleNamespace(content="plain", tool_calls=None)
    provider = OpenAIProvider(api_key="x", model="m", client=_FakeOpenAIClient(message))
    resp = await provider.complete(system="s", messages=MESSAGES)
    assert resp.text == "plain"
    assert resp.tool_calls == []
