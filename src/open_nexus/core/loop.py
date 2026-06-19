"""The ReAct agent loop — kept boring and well-instrumented.

Each turn: assemble context → persist the user turn → call the provider (with a
timeout) → if it emitted tool calls, run them through ``safety`` → feed results
back → repeat to completion → store + return the reply. Every step emits a trace
event.

The provider is anything satisfying the ``Provider`` protocol (a single adapter,
the ``ProviderRouter``, or a ``FakeProvider`` in tests). The loop never imports a
vendor SDK or a channel.
"""

from __future__ import annotations

import asyncio
import json

from open_nexus.contracts.message import Message, Role
from open_nexus.contracts.provider import Provider
from open_nexus.core.context import ContextAssembler
from open_nexus.memory.base import MemoryStore
from open_nexus.observability.events import Event
from open_nexus.observability.trace import Trace
from open_nexus.runtime.state import RuntimeState

# A hung provider must not wedge a session forever. Generous enough for slow
# models, bounded enough that a dead endpoint degrades instead of hanging.
DEFAULT_REQUEST_TIMEOUT = 60.0


async def run_turn(
    *,
    user_text: str,
    state: RuntimeState,
    provider: Provider,
    assembler: ContextAssembler,
    store: MemoryStore,
    tools=None,  # optional ToolRegistry; None in Phase 0 (no tools)
    trace: Trace | None = None,
    max_steps: int = 6,
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
) -> str:
    """Run one turn to completion and return the assistant's reply text."""
    trace = trace or Trace(state.trace_id)
    trace.emit(Event.MESSAGE_RECEIVED, session=state.session_id, channel=state.active_channel)

    # Assemble BEFORE persisting the user turn: assemble() reads prior history and
    # appends the current message itself, so persisting first would duplicate it.
    ctx = assembler.assemble(session_id=state.session_id, store=store, user_text=user_text)
    store.append_message(session_id=state.session_id, role=Role.USER, content=user_text)
    trace.emit(Event.CONTEXT_BUILT, messages=len(ctx.messages))

    messages = list(ctx.messages)
    tool_specs = tools.specs() if tools else None

    for _ in range(max_steps):
        trace.emit(Event.PROVIDER_SELECTED, provider=getattr(provider, "name", "?"))
        try:
            resp = await asyncio.wait_for(
                provider.complete(system=ctx.system, messages=messages, tools=tool_specs),
                timeout=request_timeout,
            )
        except TimeoutError:
            trace.emit(Event.ERROR, reason="provider_timeout")
            timed_out = "Sorry — the model didn't respond in time. Try again?"
            store.append_message(
                session_id=state.session_id, role=Role.ASSISTANT, content=timed_out
            )
            return timed_out
        trace.emit(Event.PROVIDER_COMPLETED, tool_calls=len(resp.tool_calls))

        if not resp.tool_calls or tools is None:
            store.append_message(
                session_id=state.session_id, role=Role.ASSISTANT, content=resp.text
            )
            trace.emit(Event.MEMORY_WRITTEN, role="assistant")
            trace.emit(Event.RESPONSE_SENT)
            return resp.text

        # Tool-using step: persist the assistant's rationale (if any) so a later
        # session sees why the tools ran, then run each call through safety.
        if resp.text:
            store.append_message(
                session_id=state.session_id, role=Role.ASSISTANT, content=resp.text
            )
        messages.append(Message(role=Role.ASSISTANT, content=resp.text))
        for call in resp.tool_calls:
            trace.emit(Event.TOOL_REQUESTED, tool=call.name)
            result = await tools.run(call, trace=trace, store=store, session_id=state.session_id)
            # Feed results back as JSON, not a Python repr, so the model gets
            # well-formed data.
            messages.append(
                Message(
                    role=Role.TOOL,
                    content=json.dumps(result, default=str),
                    tool_name=call.name,
                )
            )

    # Exhausted the step budget without a final answer.
    fallback = "I wasn't able to finish that within the step budget."
    store.append_message(session_id=state.session_id, role=Role.ASSISTANT, content=fallback)
    return fallback
