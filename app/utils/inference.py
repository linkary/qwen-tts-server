"""
Inference runner utility for non-blocking model inference.

Offloads blocking GPU inference to a thread pool via run_in_executor,
with a semaphore to control GPU concurrency and timeout-based rejection.
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar, Callable, Any

from fastapi import HTTPException

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Thread pool for offloading blocking inference calls
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tts-inference")

# Semaphore for GPU concurrency control (initialized at startup)
_semaphore: asyncio.Semaphore | None = None


def init_inference(max_concurrent: int = 1) -> None:
    """
    Initialize the inference semaphore. Must be called inside the running event loop
    (e.g. in the FastAPI lifespan handler).
    """
    global _semaphore
    _semaphore = asyncio.Semaphore(max_concurrent)
    logger.info(f"Inference runner initialized (max_concurrent={max_concurrent})")


async def run_inference(func: Callable[..., T], *args: Any, timeout: float = 300.0, **kwargs: Any) -> T:
    """
    Run a blocking inference function without blocking the event loop.

    - Waits on a semaphore to limit GPU concurrency
    - Times out with HTTP 503 if the queue wait exceeds `timeout` seconds
    - Offloads the actual call to a thread pool via run_in_executor

    Args:
        func: The blocking function to call (e.g. model.generate_custom_voice)
        *args: Positional arguments for func
        timeout: Max seconds to wait for semaphore before returning 503
        **kwargs: Keyword arguments for func

    Returns:
        The return value of func(*args, **kwargs)

    Raises:
        HTTPException(503): If the wait exceeds the timeout
    """
    if _semaphore is None:
        # Fallback: if init_inference wasn't called, run directly
        logger.warning("Inference semaphore not initialized, running synchronously")
        return func(*args, **kwargs)

    try:
        await asyncio.wait_for(_semaphore.acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=503,
            detail="Server busy — too many concurrent requests. Please retry later."
        )

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            lambda: func(*args, **kwargs)  # type: ignore[arg-type]
        )
    finally:
        _semaphore.release()
