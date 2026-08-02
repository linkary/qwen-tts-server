"""
Tests for app.utils.keyed_lock
"""
import asyncio

import pytest

from app.utils.keyed_lock import KeyedLock


@pytest.mark.unit
class TestKeyedLock:
    """Tests for KeyedLock."""

    async def test_same_key_serializes(self):
        """Holders of the same key must not overlap."""
        locks = KeyedLock()
        overlapped = False
        active = 0

        async def worker():
            nonlocal overlapped, active
            async with locks.acquire('k'):
                active += 1
                if active > 1:
                    overlapped = True
                await asyncio.sleep(0.02)
                active -= 1

        await asyncio.gather(*(worker() for _ in range(5)))

        assert overlapped is False

    async def test_different_keys_run_concurrently(self):
        """Different keys must not wait on each other."""
        locks = KeyedLock()
        peak = 0
        active = 0

        async def worker(key):
            nonlocal peak, active
            async with locks.acquire(key):
                active += 1
                peak = max(peak, active)
                await asyncio.sleep(0.02)
                active -= 1

        await asyncio.gather(*(worker(f'k{i}') for i in range(4)))

        assert peak == 4

    async def test_keys_are_released_after_use(self):
        """Idle keys must not accumulate, or a long-lived instance leaks memory."""
        locks = KeyedLock()

        async with locks.acquire('a'):
            assert locks.tracked_keys() == 1

        assert locks.tracked_keys() == 0

        await asyncio.gather(*(_hold(locks, f'k{i}') for i in range(20)))
        assert locks.tracked_keys() == 0

    async def test_key_retained_while_others_wait(self):
        """A key with queued waiters must stay tracked until the last one leaves."""
        locks = KeyedLock()
        started = asyncio.Event()
        release = asyncio.Event()

        async def holder():
            async with locks.acquire('k'):
                started.set()
                await release.wait()

        async def waiter():
            async with locks.acquire('k'):
                pass

        holder_task = asyncio.create_task(holder())
        await started.wait()
        waiter_task = asyncio.create_task(waiter())
        await asyncio.sleep(0)  # let the waiter register

        assert locks.tracked_keys() == 1

        release.set()
        await asyncio.gather(holder_task, waiter_task)
        assert locks.tracked_keys() == 0

    async def test_exception_releases_lock(self):
        """A failing holder must not wedge the key."""
        locks = KeyedLock()

        with pytest.raises(ValueError):
            async with locks.acquire('k'):
                raise ValueError('boom')

        assert locks.tracked_keys() == 0

        # The key must still be usable.
        async with locks.acquire('k'):
            pass

    async def test_cancellation_releases_lock(self):
        """A cancelled holder must not wedge the key."""
        locks = KeyedLock()
        started = asyncio.Event()

        async def holder():
            async with locks.acquire('k'):
                started.set()
                await asyncio.sleep(10)

        task = asyncio.create_task(holder())
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert locks.tracked_keys() == 0
        async with locks.acquire('k'):
            pass


async def _hold(locks: KeyedLock, key: str) -> None:
    async with locks.acquire(key):
        await asyncio.sleep(0)
