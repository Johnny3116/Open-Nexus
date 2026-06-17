"""Entrypoint — wire the harness and start it.

Phase 0 default: terminal → gateway → core loop → EchoProvider → SQLite → reply,
with zero cloud setup. Point ``config.yaml`` at a real provider/memory backend.

    open-nexus chat            # start the terminal channel
    open-nexus serve           # start the HTTP API (needs the `web` extra)
    open-nexus version
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from open_nexus import __version__
from open_nexus.channels.terminal import TerminalChannel
from open_nexus.config import Config, load_config
from open_nexus.core.context import ContextAssembler
from open_nexus.gateway.router import Gateway
from open_nexus.memory.factory import build_store
from open_nexus.providers.factory import build_router


def build_gateway(cfg: Config) -> Gateway:
    """Assemble a Gateway from config. Shared by the chat and serve entrypoints."""
    return Gateway(
        provider=build_router(cfg),
        store=build_store(cfg),
        assembler=ContextAssembler(identity_dir=cfg.identity_dir),
        active_model=cfg.routing.default,
    )


async def _chat(config_path: str) -> int:
    cfg = load_config(config_path)
    gateway = build_gateway(cfg)
    print(f"Open-Nexus ready (model: {cfg.routing.default}). Ctrl-D or /quit to exit.")
    await gateway.run(TerminalChannel())
    return 0


def _serve(config_path: str, host: str, port: int) -> int:
    import uvicorn  # requires the `web` extra

    from open_nexus.api.server import build_app

    app = build_app(build_gateway(load_config(config_path)))
    uvicorn.run(app, host=host, port=port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="open-nexus", description="Open-Nexus harness")
    sub = parser.add_subparsers(dest="command")
    chat = sub.add_parser("chat", help="start the terminal channel")
    chat.add_argument("--config", default="config.yaml")
    serve = sub.add_parser("serve", help="start the HTTP API")
    serve.add_argument("--config", default="config.yaml")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8800)
    sub.add_parser("version", help="print version")

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command in (None, "version"):
        print(f"open-nexus {__version__}")
        return 0
    if args.command == "chat":
        return asyncio.run(_chat(args.config))
    if args.command == "serve":
        return _serve(args.config, args.host, args.port)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
