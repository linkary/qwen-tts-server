"""
Inference runner for bounded-concurrency, non-blocking model inference.

Offloads blocking GPU inference to a worker thread and caps how many inferences
may run at once, so the event loop stays responsive and the GPU is never
oversubscribed.

The invariant this module exists to hold: at most ``max_concurrent`` inference
calls are executing at any instant. Keeping it is subtler than it looks, because
a work item already running in a thread cannot be cancelled. Releasing the
permit from the awaiting coroutine — the shape a ``finally`` around
``run_in_executor`` produces — hands the permit to the next request while the
previous inference is still on the GPU. On a single device that is two
concurrent forward passes, each allocating its own KV cache.

Measured under a raw ``asyncio.Task.cancel()`` with ``max_concurrent=1``, which
is how cancellation actually arrives in this server (Starlette client
disconnects, uvicorn shutdown, any enclosing ``asyncio.timeout``):

    permit released in the coroutine's finally      -> peak concurrency 2
    anyio.to_thread.run_sync(..., limiter=limiter)  -> peak concurrency 2
    permit released from the worker thread          -> peak concurrency 1

anyio's ``abandon_on_cancel=False`` and its ``limiter=`` parameter defer only
*anyio-level* cancel scopes; neither shields against a plain asyncio cancel, so
neither is sufficient here. The permit is therefore acquired on behalf of an
opaque borrower token and released from inside the worker thread via
``call_soon_threadsafe``, making its lifetime exactly the inference's lifetime
no matter how the caller ends. A cancelled caller returns immediately rather
than blocking on an uninterruptible GPU call; the permit frees when the GPU
does.

``loop.run_in_executor`` is used rather than ``anyio.to_thread.run_sync``
because it submits the work item synchronously. There is no await between taking
the permit and queueing the thread, which removes the window in which a
cancellation could strand a permit that no thread will ever release.

It also uses the event loop's own executor, which ``asyncio.run`` drains as part
of loop shutdown. A module-level ``ThreadPoolExecutor`` of non-daemon threads is
instead joined by ``atexit``, i.e. *after* the loop and the server are already
gone: measured with a 3s inference in flight at shutdown, the loop closed at
0.20s but the process did not exit until 3.00s, with that 2.8s invisible to the
framework. This does not make shutdown faster — a running native call cannot be
interrupted, so an in-flight inference delays exit either way — it moves the
wait into the phase where uvicorn's graceful-shutdown timeout can observe and
bound it.

Timeout semantics: the timeout bounds the QUEUE WAIT only. Once a request is
admitted, its inference runs without a deadline. This is deliberate — a native
CUDA call cannot be preempted from Python, so a deadline on execution could not
stop a hung inference; it could only make the caller pay the full GPU cost and
then still receive a 503. A permit held indefinitely is instead surfaced by
:func:`get_inference_stats` (see ``/health/inference``) so an orchestrator can
act on it.
"""
import asyncio
import logging
from functools import partial
from typing import Any, Callable, TypeVar

import anyio
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Hint given to clients rejected with a 503. Short, because a rejection means
# the queue was already full for the whole timeout window.
RETRY_AFTER_SECONDS = 5

# Caps concurrent inferences. Created lazily so that importing this module has
# no side effects and so that an entry point which skips the lifespan handler
# still gets a bounded limiter rather than unlimited concurrency.
_limiter: anyio.CapacityLimiter | None = None

# Ops counter: requests shed with a 503. Mutated only from the event loop
# thread, so no lock is needed.
_rejected_requests = 0


def init_inference(max_concurrent: int | None = None) -> None:
    """
    Configure the inference concurrency limit.

    Safe to call more than once; an existing limiter is retuned in place rather
    than replaced, so in-flight requests keep their permits.

    Args:
        max_concurrent: Permit count. Defaults to settings.max_concurrent_inferences.
    """
    global _limiter

    if max_concurrent is None:
        max_concurrent = settings.max_concurrent_inferences

    if _limiter is None:
        _limiter = anyio.CapacityLimiter(max_concurrent)
    else:
        _limiter.total_tokens = max_concurrent

    logger.info(f'Inference runner initialized (max_concurrent={max_concurrent})')


def _resolve_limiter() -> anyio.CapacityLimiter:
    """
    Return the limiter, creating it from settings if the lifespan never ran.

    Falling back to a configured limiter — rather than running unbounded — keeps
    the concurrency invariant intact for entry points that bypass the lifespan
    handler (ASGI sub-mounts, ``--lifespan off``, scripts importing ``app``).
    The warning marks it as a setup the deployment should fix.
    """
    global _limiter

    if _limiter is None:
        logger.warning(
            'Inference limiter was not initialized by the lifespan handler; '
            'creating it lazily from settings '
            f'(max_concurrent={settings.max_concurrent_inferences}). '
            'Ensure the app is started with its lifespan enabled.'
        )
        init_inference()

    assert _limiter is not None  # narrowed by init_inference
    return _limiter


async def run_inference(
    func: Callable[..., T],
    *args: Any,
    timeout: float | None = None,
    **kwargs: Any,
) -> T:
    """
    Run a blocking inference function without blocking the event loop.

    Waits for a concurrency permit, then executes ``func`` in a worker thread.
    The permit is held for exactly as long as ``func`` runs, including when the
    caller is cancelled mid-inference.

    Args:
        func: The blocking function to call (e.g. model.generate_custom_voice).
        *args: Positional arguments for func.
        timeout: Max seconds to wait for a permit. Defaults to
            settings.inference_queue_timeout_seconds. Does not bound execution.
        **kwargs: Keyword arguments for func.

    Returns:
        The return value of func(*args, **kwargs).

    Raises:
        HTTPException(503): If the queue wait exceeds the timeout.
    """
    global _rejected_requests

    limiter = _resolve_limiter()

    if timeout is None:
        timeout = settings.inference_queue_timeout_seconds

    # An opaque borrower rather than the calling task, so the permit can be
    # returned from the worker thread and is not tied to task identity.
    borrower = object()

    try:
        with anyio.fail_after(timeout):
            await limiter.acquire_on_behalf_of(borrower)
    except TimeoutError:
        _rejected_requests += 1
        logger.warning(
            f'Shedding request after {timeout:.1f}s queue wait: '
            f'{limiter.borrowed_tokens}/{limiter.total_tokens} inferences in '
            f'flight, {_queued_requests(limiter)} still queued '
            f'({_rejected_requests} shed since start)'
        )
        raise HTTPException(
            status_code=503,
            detail='Server busy — too many concurrent requests. Please retry later.',
            headers={'Retry-After': str(RETRY_AFTER_SECONDS)},
        )

    loop = asyncio.get_running_loop()

    def release() -> None:
        limiter.release_on_behalf_of(borrower)

    def guarded() -> T:
        try:
            # partial() keeps *args/**kwargs typed, unlike a closure over a lambda.
            return partial(func, *args, **kwargs)()
        finally:
            # Released here, not in this coroutine, so the permit outlives a
            # cancelled caller for as long as the GPU is still busy.
            loop.call_soon_threadsafe(release)

    try:
        future = loop.run_in_executor(None, guarded)
    except RuntimeError:
        # Executor already shut down: no thread will run, so release here.
        release()
        raise

    return await future


def _queued_requests(limiter: anyio.CapacityLimiter) -> int:
    """Number of requests waiting for a permit."""
    return limiter.statistics().tasks_waiting


def get_inference_stats() -> dict[str, Any]:
    """
    Snapshot of inference concurrency state, for health and capacity checks.

    ``in_flight`` pinned at ``max_concurrent`` together with a non-zero
    ``queued`` and a climbing ``rejected_total`` is the signature of an
    inference that is not returning.
    """
    if _limiter is None:
        return {
            'initialized': False,
            'max_concurrent': settings.max_concurrent_inferences,
            'in_flight': 0,
            'queued': 0,
            'rejected_total': _rejected_requests,
            'queue_timeout_seconds': settings.inference_queue_timeout_seconds,
        }

    return {
        'initialized': True,
        'max_concurrent': int(_limiter.total_tokens),
        'in_flight': int(_limiter.borrowed_tokens),
        'queued': _queued_requests(_limiter),
        'rejected_total': _rejected_requests,
        'queue_timeout_seconds': settings.inference_queue_timeout_seconds,
    }


def reset_inference_state() -> None:
    """Drop the limiter and counters. For tests only."""
    global _limiter, _rejected_requests
    _limiter = None
    _rejected_requests = 0
