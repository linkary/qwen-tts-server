"""
Tests for app.utils.inference module
"""
import asyncio
import threading
import time

import pytest
from fastapi import HTTPException

from app.utils.inference import (
    get_inference_stats,
    init_inference,
    reset_inference_state,
    run_inference,
)


@pytest.fixture(autouse=True)
def reset_inference():
    """Reset the inference module state before and after each test."""
    reset_inference_state()
    yield
    reset_inference_state()


class ConcurrencyProbe:
    """Records the peak number of simultaneously executing calls."""

    def __init__(self, duration: float = 0.2):
        self.duration = duration
        self.peak = 0
        self._running = 0
        self._guard = threading.Lock()

    def __call__(self, value=None):
        with self._guard:
            self._running += 1
            self.peak = max(self.peak, self._running)
        time.sleep(self.duration)
        with self._guard:
            self._running -= 1
        return value


@pytest.mark.unit
class TestInitInference:
    """Tests for init_inference function."""

    def test_init_sets_max_concurrent(self):
        """init_inference caps concurrency at the requested permit count."""
        init_inference(max_concurrent=3)
        assert get_inference_stats()['max_concurrent'] == 3

    def test_init_defaults_to_settings(self):
        """Omitting max_concurrent falls back to the configured value."""
        from app.config import settings

        init_inference()
        assert get_inference_stats()['max_concurrent'] == settings.max_concurrent_inferences

    def test_init_is_idempotent(self):
        """Re-initializing retunes the existing limiter instead of replacing it."""
        init_inference(max_concurrent=1)
        init_inference(max_concurrent=4)
        assert get_inference_stats()['max_concurrent'] == 4


@pytest.mark.unit
class TestRunInference:
    """Tests for run_inference function."""

    async def test_runs_blocking_function(self):
        """run_inference should execute a blocking function and return its result."""
        init_inference(max_concurrent=1)

        def blocking_func(x, y):
            return x + y

        assert await run_inference(blocking_func, 3, 5) == 8

    async def test_runs_with_kwargs(self):
        """run_inference should pass keyword arguments correctly."""
        init_inference(max_concurrent=1)

        def blocking_func(text, language='English'):
            return f'{text}:{language}'

        result = await run_inference(blocking_func, 'hello', language='Chinese')
        assert result == 'hello:Chinese'

    async def test_does_not_block_event_loop(self):
        """Two permitted calls should overlap rather than serialize."""
        init_inference(max_concurrent=2)
        probe = ConcurrencyProbe(duration=0.2)

        start = time.monotonic()
        results = await asyncio.gather(
            run_inference(probe, 'a'),
            run_inference(probe, 'b'),
        )
        elapsed = time.monotonic() - start

        assert results == ['a', 'b']
        assert probe.peak == 2
        # Serialized execution would take ~0.4s; overlapped takes ~0.2s. The
        # bound is deliberately loose — this asserts overlap, not a latency SLO.
        assert elapsed < 0.35

    async def test_limits_concurrency(self):
        """With max_concurrent=1, calls must not overlap."""
        init_inference(max_concurrent=1)
        probe = ConcurrencyProbe(duration=0.15)

        await asyncio.gather(run_inference(probe), run_inference(probe))

        assert probe.peak == 1

    async def test_permit_not_released_until_thread_finishes(self):
        """
        Regression: cancelling a caller must not hand its permit to the next
        request while the inference is still running.

        A `finally: release()` around a bare run_in_executor releases as soon as
        the awaiting task is cancelled, but a work item already running in a
        thread cannot be cancelled — so the next request was admitted while the
        previous inference still held the GPU. On a single device that is two
        concurrent forward passes, each allocating its own KV cache.
        """
        init_inference(max_concurrent=1)
        probe = ConcurrencyProbe(duration=0.3)

        first = asyncio.create_task(run_inference(probe))
        await asyncio.sleep(0.08)  # let it reach the worker thread
        first.cancel()

        second = asyncio.create_task(run_inference(probe))

        with pytest.raises(asyncio.CancelledError):
            await first
        await second

        assert probe.peak == 1

    async def test_timeout_returns_503_with_retry_after(self):
        """When the queue wait exceeds the timeout, shed the request with a 503."""
        init_inference(max_concurrent=1)

        holder = asyncio.create_task(run_inference(ConcurrencyProbe(duration=0.6)))
        await asyncio.sleep(0.05)  # let the holder take the only permit

        with pytest.raises(HTTPException) as exc_info:
            await run_inference(lambda: None, timeout=0.1)

        assert exc_info.value.status_code == 503
        assert 'busy' in exc_info.value.detail.lower()
        # Without Retry-After, clients and proxies have no backoff hint.
        assert exc_info.value.headers['Retry-After']

        await holder

    async def test_timeout_defaults_to_configured_value(self):
        """Callers that omit `timeout` get the operator's configured value."""
        from app.config import settings

        init_inference(max_concurrent=1)
        assert (
            get_inference_stats()['queue_timeout_seconds']
            == settings.inference_queue_timeout_seconds
        )

    async def test_lazy_limiter_when_not_initialized(self):
        """
        Without init_inference, concurrency must still be bounded.

        Running unbounded here would mean any entry point that skips the lifespan
        handler (ASGI sub-mount, --lifespan off, a script importing `app`)
        silently reverts to unlimited concurrent GPU calls on the event loop.
        """
        probe = ConcurrencyProbe(duration=0.15)

        await asyncio.gather(run_inference(probe), run_inference(probe))

        assert get_inference_stats()['initialized'] is True
        assert probe.peak == 1  # bounded by the default max_concurrent of 1

    async def test_propagates_exceptions(self):
        """run_inference should propagate exceptions from the target function."""
        init_inference(max_concurrent=1)

        def failing_func():
            raise ValueError('test error')

        with pytest.raises(ValueError, match='test error'):
            await run_inference(failing_func)

    async def test_permit_released_on_exception(self):
        """A failing inference must not leak its permit."""
        init_inference(max_concurrent=1)

        def failing_func():
            raise RuntimeError('boom')

        with pytest.raises(RuntimeError):
            await run_inference(failing_func)

        assert get_inference_stats()['in_flight'] == 0
        assert await run_inference(lambda: 'ok') == 'ok'


@pytest.mark.unit
class TestInferenceStats:
    """Tests for get_inference_stats, which makes a wedged inference detectable."""

    def test_stats_before_initialization(self):
        """Stats are reportable before the limiter exists."""
        stats = get_inference_stats()
        assert stats['initialized'] is False
        assert stats['in_flight'] == 0
        assert stats['queued'] == 0

    async def test_stats_report_in_flight_and_queued(self):
        """
        Saturation must be visible: /health stays green while all permits are
        held, so this is the only signal that distinguishes busy from stuck.
        """
        init_inference(max_concurrent=1)

        holder = asyncio.create_task(run_inference(ConcurrencyProbe(duration=0.4)))
        waiter = asyncio.create_task(run_inference(ConcurrencyProbe(duration=0.05)))
        await asyncio.sleep(0.1)

        stats = get_inference_stats()
        assert stats['in_flight'] == 1
        assert stats['queued'] == 1

        await asyncio.gather(holder, waiter)
        assert get_inference_stats()['in_flight'] == 0

    async def test_rejections_are_counted(self):
        """Shed requests increment a counter so load shedding is observable."""
        init_inference(max_concurrent=1)
        assert get_inference_stats()['rejected_total'] == 0

        holder = asyncio.create_task(run_inference(ConcurrencyProbe(duration=0.4)))
        await asyncio.sleep(0.05)

        with pytest.raises(HTTPException):
            await run_inference(lambda: None, timeout=0.05)

        assert get_inference_stats()['rejected_total'] == 1
        await holder
