"""
Structural tests for router exception handling.

`HTTPException` subclasses `Exception`, so a handler shaped like

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

silently rewrites every deliberate status code raised inside its `try` block
into a 500 — including the 503 that signals a saturated inference queue. Load
balancers, SDK retry policies and Kubernetes probes keyed on 503 do not retry a
500, and the accompanying `logger.error` pages on-call for routine saturation.

These tests assert the shape of the source rather than the behaviour of a live
request, so they cover every endpoint (including streaming ones) without needing
a GPU, a model, or torch installed — the reason the original defect was
invisible to CI.
"""
import ast
from pathlib import Path

import pytest

ROUTERS_DIR = Path(__file__).resolve().parents[2] / 'app' / 'routers'


def _handler_types(handler: ast.ExceptHandler) -> str | None:
    """Name of the exception type an `except` clause catches, if it is a bare name."""
    if handler.type is None:
        return None
    if isinstance(handler.type, ast.Name):
        return handler.type.id
    return ast.dump(handler.type)


def _raises_status(handler: ast.ExceptHandler, status: int) -> bool:
    """Whether the handler raises HTTPException with the given status code."""
    for node in ast.walk(handler):
        if not (isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'HTTPException'):
            continue
        for keyword in node.keywords:
            if (
                keyword.arg == 'status_code'
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value == status
            ):
                return True
    return False


def _catch_all_try_blocks() -> list[tuple[str, int, list[str | None]]]:
    """Every try block in the routers that converts a caught Exception into a 500."""
    found = []
    for path in sorted(ROUTERS_DIR.glob('*.py')):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            if any(
                _handler_types(h) == 'Exception' and _raises_status(h, 500)
                for h in node.handlers
            ):
                found.append((path.name, node.lineno, [_handler_types(h) for h in node.handlers]))
    return found


def _calls_run_inference(node: ast.AST) -> bool:
    """Whether the subtree awaits run_inference or the prompt resolver."""
    targets = {'run_inference', 'get_or_create_voice_prompt'}
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and getattr(child.func, 'id', None) in targets:
            return True
    return False


@pytest.mark.unit
class TestRouterErrorHandling:
    """Ensures deliberate status codes survive the routers' catch-all handlers."""

    def test_catch_all_blocks_exist_to_check(self):
        """Guard against the checks below passing because they found nothing."""
        assert _catch_all_try_blocks(), 'no catch-all handlers found — checks are vacuous'

    def test_inference_endpoints_preserve_http_exceptions(self):
        """
        Any try block that runs an inference and catches Exception must re-raise
        HTTPException first, or the queue-full 503 is reported as a 500.
        """
        offenders = []
        for path in sorted(ROUTERS_DIR.glob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Try) or not _calls_run_inference(node):
                    continue
                catches_all = any(
                    _handler_types(h) == 'Exception' and _raises_status(h, 500)
                    for h in node.handlers
                )
                if not catches_all:
                    continue
                guards = [h for h in node.handlers if _handler_types(h) == 'HTTPException']
                if not guards or _handler_types(node.handlers[0]) != 'HTTPException':
                    offenders.append(f'{path.name}:{node.lineno}')

        assert offenders == [], (
            'try blocks run an inference and rewrite HTTPException to 500; add '
            f'`except HTTPException: raise` before the catch-all: {offenders}'
        )

    def test_http_exception_guard_only_re_raises(self):
        """The guard must be a plain `raise`, not a re-wrap that changes the code."""
        for path in sorted(ROUTERS_DIR.glob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Try):
                    continue
                for handler in node.handlers:
                    if _handler_types(handler) != 'HTTPException':
                        continue
                    statements = [s for s in handler.body if not isinstance(s, ast.Pass)]
                    assert len(statements) == 1, (
                        f'{path.name}:{handler.lineno}: HTTPException guard should '
                        'only re-raise'
                    )
                    assert isinstance(statements[0], ast.Raise), (
                        f'{path.name}:{handler.lineno}: HTTPException guard must raise'
                    )
                    assert statements[0].exc is None, (
                        f'{path.name}:{handler.lineno}: use a bare `raise` so the '
                        'original status code and detail are preserved'
                    )
