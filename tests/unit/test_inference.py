"""
Tests for app.utils.inference module
"""
import asyncio
import time
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.utils.inference import init_inference, run_inference, _semaphore


@pytest.fixture(autouse=True)
def reset_inference():
    """Reset the inference module state before each test."""
    import app.utils.inference as inf
    inf._semaphore = None
    yield
    inf._semaphore = None


class TestInitInference:
    """Tests for init_inference function."""

    def test_init_creates_semaphore(self):
        """init_inference creates a semaphore with the specified max_concurrent."""
        init_inference(max_concurrent=3)
        import app.utils.inference as inf
        assert inf._semaphore is not None
        # Semaphore should have the correct initial value
        assert inf._semaphore._value == 3

    def test_init_default_max_concurrent(self):
        """init_inference defaults to max_concurrent=1."""
        init_inference()
        import app.utils.inference as inf
        assert inf._semaphore._value == 1


class TestRunInference:
    """Tests for run_inference function."""

    @pytest.mark.asyncio
    async def test_runs_blocking_function(self):
        """run_inference should execute a blocking function and return its result."""
        init_inference(max_concurrent=1)

        def blocking_func(x, y):
            return x + y

        result = await run_inference(blocking_func, 3, 5, timeout=5.0)
        assert result == 8

    @pytest.mark.asyncio
    async def test_runs_with_kwargs(self):
        """run_inference should pass keyword arguments correctly."""
        init_inference(max_concurrent=1)

        def blocking_func(text, language="English"):
            return f"{text}:{language}"

        result = await run_inference(blocking_func, "hello", language="Chinese", timeout=5.0)
        assert result == "hello:Chinese"

    @pytest.mark.asyncio
    async def test_does_not_block_event_loop(self):
        """run_inference should not block the event loop during execution."""
        init_inference(max_concurrent=2)

        def slow_func():
            time.sleep(0.2)
            return "done"

        # Run two tasks concurrently - if event loop were blocked,
        # this would take 0.4s; with thread pool it should take ~0.2s
        start = time.monotonic()
        results = await asyncio.gather(
            run_inference(slow_func, timeout=5.0),
            run_inference(slow_func, timeout=5.0),
        )
        elapsed = time.monotonic() - start

        assert results == ["done", "done"]
        # Should complete in roughly 0.2s, not 0.4s
        assert elapsed < 0.35

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """With max_concurrent=1, two calls should serialize."""
        init_inference(max_concurrent=1)

        call_order = []

        def slow_func(name):
            call_order.append(f"{name}_start")
            time.sleep(0.15)
            call_order.append(f"{name}_end")
            return name

        results = await asyncio.gather(
            run_inference(slow_func, "A", timeout=5.0),
            run_inference(slow_func, "B", timeout=5.0),
        )

        assert set(results) == {"A", "B"}
        # With semaphore=1, one must complete before the other starts
        # So the pattern should be: X_start, X_end, Y_start, Y_end
        assert call_order[1].endswith("_end")  # First task ends before second starts

    @pytest.mark.asyncio
    async def test_timeout_returns_503(self):
        """When semaphore wait exceeds timeout, should raise HTTPException 503."""
        init_inference(max_concurrent=1)

        def slow_func():
            time.sleep(1.0)
            return "done"

        # First call acquires the semaphore
        task1 = asyncio.create_task(run_inference(slow_func, timeout=5.0))
        # Give task1 a moment to acquire the semaphore
        await asyncio.sleep(0.05)

        # Second call should timeout waiting for the semaphore
        with pytest.raises(HTTPException) as exc_info:
            await run_inference(slow_func, timeout=0.1)

        assert exc_info.value.status_code == 503
        assert "busy" in exc_info.value.detail.lower()

        # Clean up
        await task1

    @pytest.mark.asyncio
    async def test_fallback_without_init(self):
        """Without init_inference, run_inference should fall back to sync execution."""
        def simple_func(x):
            return x * 2

        result = await run_inference(simple_func, 5, timeout=5.0)
        assert result == 10

    @pytest.mark.asyncio
    async def test_propagates_exceptions(self):
        """run_inference should propagate exceptions from the target function."""
        init_inference(max_concurrent=1)

        def failing_func():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await run_inference(failing_func, timeout=5.0)

    @pytest.mark.asyncio
    async def test_semaphore_released_on_exception(self):
        """Semaphore should be released even if the function raises."""
        init_inference(max_concurrent=1)

        def failing_func():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await run_inference(failing_func, timeout=5.0)

        # Semaphore should be released — next call should work
        def ok_func():
            return "ok"

        result = await run_inference(ok_func, timeout=5.0)
        assert result == "ok"
