"""Minimal in-memory sliding-window rate limiter (per process)."""

import threading
import time
from collections import defaultdict, deque


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        super().__init__("Rate limit exceeded")
        self.retry_after = retry_after


class SlidingWindowLimiter:
    def __init__(self):
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window: int) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= window:
                hits.popleft()

            if len(hits) >= limit:
                retry_after = max(1, int(window - (now - hits[0])) + 1)
                raise RateLimitExceeded(retry_after)

            hits.append(now)

            # Drop idle keys so the dict cannot grow without bound.
            if len(self._hits) > 10_000:
                for k in [k for k, v in self._hits.items() if not v]:
                    del self._hits[k]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
