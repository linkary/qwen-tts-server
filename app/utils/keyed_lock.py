"""
Per-key asyncio mutual exclusion.
"""
import asyncio
from collections import Counter
from contextlib import asynccontextmanager
from typing import AsyncIterator, Hashable


class KeyedLock:
    """
    Serialize async work per key, with automatic cleanup of idle keys.

    Requests holding different keys never wait on each other; requests sharing a
    key run one at a time. Used to collapse a stampede of identical concurrent
    requests into a single expensive computation ("single flight"): the first
    holder computes and publishes the result, and every request that queued
    behind it re-checks the published result instead of recomputing.

    Locks are reference-counted and dropped once no task holds or awaits them,
    so a long-lived instance does not accumulate an entry per distinct key.

    Safe under asyncio because every mutation below happens without an
    intervening await, and therefore cannot interleave with another task.
    """

    def __init__(self) -> None:
        self._locks: dict[Hashable, asyncio.Lock] = {}
        self._users: Counter = Counter()

    @asynccontextmanager
    async def acquire(self, key: Hashable) -> AsyncIterator[None]:
        """Hold the lock for ``key`` for the duration of the ``async with`` block."""
        lock = self._locks.setdefault(key, asyncio.Lock())
        self._users[key] += 1
        try:
            async with lock:
                yield
        finally:
            self._users[key] -= 1
            if not self._users[key]:
                del self._users[key]
                self._locks.pop(key, None)

    def tracked_keys(self) -> int:
        """Number of keys currently held or awaited. For tests and diagnostics."""
        return len(self._locks)
