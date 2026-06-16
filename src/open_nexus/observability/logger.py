"""Structured logging helper.

Phase 0 keeps it to stdlib ``logging`` with a consistent format. Swap the handler
for JSON/OTel later without touching call sites.
"""

from __future__ import annotations

import logging

_CONFIGURED = False


def _configure() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    _CONFIGURED = True


def get_logger(name: str = "open_nexus") -> logging.Logger:
    _configure()
    return logging.getLogger(name)
