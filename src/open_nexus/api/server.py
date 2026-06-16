"""FastAPI server (stub) — the shared runtime API.

Built in the Persistent-Nexus phase. Defined here so the surface is visible and
the gateway can be reused behind it. Requires the ``web`` extra (fastapi/uvicorn).
"""

from __future__ import annotations


def build_app(gateway):
    """Return a FastAPI app exposing the v1 API over the given Gateway."""
    # TODO(phase: persistent): from fastapi import FastAPI; define routes:
    #   POST /v1/messages, GET /v1/sessions/{id}, GET /health
    raise NotImplementedError("api.server.build_app: persistent-nexus phase")
