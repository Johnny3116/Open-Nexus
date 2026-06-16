"""Observability — traces and structured events from day one.

Once Nexus has memory, tools, and multiple providers, "why did it do that?" is
unanswerable without a trace. Every major lifecycle event (see ``events.Event``)
is logged with the turn's ``trace_id`` so a turn can be reconstructed end to end.
"""

from open_nexus.observability.events import Event
from open_nexus.observability.logger import get_logger
from open_nexus.observability.trace import Trace

__all__ = ["Event", "Trace", "get_logger"]
