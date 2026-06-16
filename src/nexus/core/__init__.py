"""Nexus Core — the long-lived harness process.

Standard, boring, well-instrumented ReAct loop:

    input -> assemble context -> call provider -> run tool calls (through the
    approval gate) -> feed results back -> repeat -> reply on the originating
    channel.

A per-session queue serialises concurrent messages so "a message arrives
mid-run" is handled cleanly.
"""
