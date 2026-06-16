"""The agent loop.

Each turn:
    1. resolve session (who / which channel)
    2. assemble context (SOUL.md + USER.md/TOOLS.md + Layer-1 memory + retrieval)
    3. call the active provider (with fallback chain)
    4. if the model emitted tool calls, run them through the approval gate
    5. feed results back; repeat until the model is done
    6. emit the reply on the originating channel; persist the turn to memory

Phase 0 goal: prove input -> context -> model -> reply -> store works end to end
on the terminal channel against one provider.
"""

from __future__ import annotations


def run_channel(channel: str, config_path: str = "config/nexus.toml") -> int:
    """Boot Core and attach a single channel adapter.

    This is the Phase-0 happy path entry point called by the CLI.
    """
    from nexus.config import load_config

    try:
        config = load_config(config_path)
    except FileNotFoundError as exc:
        print(f"error: {exc}")
        return 1

    # TODO(phase-0): construct the real wiring:
    #   provider   = build_provider(config)
    #   memory     = build_memory(config)
    #   assembler  = ContextAssembler(identity_dir=..., memory=memory)
    #   adapter    = build_channel(channel, config)
    #   then: for inbound in adapter.listen(): await agent_turn(...)
    print(
        f"[nexus] Core booting with channel={channel!r} "
        f"(config loaded: {bool(config)}). Loop not yet implemented — see TODOs."
    )
    return 0


async def agent_turn(*, session, message, provider, assembler, tools, memory) -> str:
    """Run a single ReAct turn to completion and return the reply text.

    Pseudocode for the loop the rest of the package plugs into:

        ctx = assembler.assemble(session, message)
        while True:
            resp = await provider.complete(ctx)
            if not resp.tool_calls:
                memory.append(session, "assistant", resp.text)
                return resp.text
            for call in resp.tool_calls:
                result = await tools.run(call)   # runs through the approval gate
                ctx.add_tool_result(call, result)
    """
    raise NotImplementedError("agent_turn: implemented in Phase 0")
