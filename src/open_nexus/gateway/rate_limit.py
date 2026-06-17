"""Rate limiting — a simple per-user token bucket.

Keeps a runaway client (or a loop bug) from hammering providers. Phase 0 wires a
generous default; tune per channel later.
"""

from __future__ import annotations

import time
from collections import defaultdict


class RateLimited(Exception):
    """Raised when a user exceeds their token bucket."""


class TokenBucket:
    def __init__(self, *, capacity: int = 30, refill_per_sec: float = 0.5) -> None:
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self._tokens: dict[str, float] = defaultdict(lambda: float(capacity))
        self._last: dict[str, float] = defaultdict(time.monotonic)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        self._tokens[key] = min(
            self.capacity, self._tokens[key] + (now - self._last[key]) * self.refill_per_sec
        )
        self._last[key] = now
        if self._tokens[key] >= 1:
            self._tokens[key] -= 1
            return True
        return False
