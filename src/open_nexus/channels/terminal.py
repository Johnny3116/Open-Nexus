"""Terminal channel — the Phase-0 surface. Stdin in, stdout out.

A dumb adapter: it yields InboundMessages and prints OutboundMessages. It knows
nothing about auth or sessions — the gateway handles those.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator

from open_nexus.channels.base import BaseChannel
from open_nexus.contracts.channel import InboundMessage, OutboundMessage

LOCAL_USER_ID = "local"


class TerminalChannel(BaseChannel):
    name = "terminal"

    def __init__(self, *, prompt: str = "you> ") -> None:
        self._prompt = prompt

    async def listen(self) -> AsyncIterator[InboundMessage]:
        loop = asyncio.get_running_loop()
        while True:
            # Read stdin off the event loop so the loop stays responsive.
            sys.stdout.write(self._prompt)
            sys.stdout.flush()
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:  # EOF (Ctrl-D)
                break
            text = line.rstrip("\n")
            if text.strip() in {"/quit", "/exit"}:
                break
            yield InboundMessage(channel=self.name, channel_user_id=LOCAL_USER_ID, text=text)

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        sys.stdout.write(f"nexus> {message.text}\n")
        sys.stdout.flush()
