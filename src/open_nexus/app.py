"""Entrypoint — wire the harness and start it.

Phase 0 default: terminal → gateway → core loop → EchoProvider → SQLite → reply,
with zero cloud setup. Point ``config.yaml`` at a real provider to use Claude etc.

    open-nexus chat            # start the terminal channel
    open-nexus version
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from open_nexus import __version__
from open_nexus.channels.terminal import TerminalChannel
from open_nexus.config import load_config
from open_nexus.core.context import ContextAssembler
from open_nexus.gateway.router import Gateway
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.providers.factory import build_router


async def _chat(config_path: str) -> int:
    cfg = load_config(config_path)
    provider = build_router(cfg)
    store = SQLiteStore(cfg.memory_path)
    gateway = Gateway(
        provider=provider,
        store=store,
        assembler=ContextAssembler(identity_dir=cfg.identity_dir),
        active_model=cfg.routing.default,
    )
    print(f"Open-Nexus ready (model: {cfg.routing.default}). Ctrl-D or /quit to exit.")
    await gateway.run(TerminalChannel())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="open-nexus", description="Open-Nexus harness")
    sub = parser.add_subparsers(dest="command")
    chat = sub.add_parser("chat", help="start the terminal channel")
    chat.add_argument("--config", default="config.yaml")
    sub.add_parser("version", help="print version")

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command in (None, "version"):
        print(f"open-nexus {__version__}")
        return 0
    if args.command == "chat":
        return asyncio.run(_chat(args.config))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
