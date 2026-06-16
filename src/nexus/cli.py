"""Nexus CLI entry point.

Usage:
    nexus run --channel terminal      # start Core with a channel attached
    nexus model <name>                # switch the active provider/model
    nexus version

Phase 0 wires up `run --channel terminal` end-to-end. Other subcommands are
stubs that print intent until their phase lands.
"""

from __future__ import annotations

import argparse
import sys

from nexus import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nexus", description="Nexus agent harness")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="start Core with a channel")
    run.add_argument("--channel", default="terminal", help="channel to attach (default: terminal)")
    run.add_argument("--config", default="config/nexus.toml", help="path to config")

    model = sub.add_parser("model", help="switch the active model")
    model.add_argument("name", help="provider/model key from config")

    sub.add_parser("version", help="print version")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv if argv is not None else sys.argv[1:])

    if args.command == "version" or args.command is None:
        print(f"nexus {__version__}")
        return 0

    if args.command == "run":
        # Lazy import so `nexus version` works without runtime deps installed.
        from nexus.core.loop import run_channel

        return run_channel(channel=args.channel, config_path=args.config)

    if args.command == "model":
        print(f"TODO(phase-1): switch active model to {args.name!r} and persist it.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
