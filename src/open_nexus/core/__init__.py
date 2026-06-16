"""Core — the harness's brain: context assembly, sessions, the agent loop.

Core knows nothing about Discord/Telegram/terminal/web (the gateway adapts those)
nor about any specific vendor API (providers adapt those). It assembles context,
calls a ``Provider``, runs any tool calls through ``safety``, and replies.
"""
