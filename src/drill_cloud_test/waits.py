from __future__ import annotations

import time
from collections.abc import Callable

from playwright.sync_api import Page


def wait_until(page: Page, predicate: Callable[[], bool], *, timeout_ms: int, description: str) -> None:
    """Poll Python-side browser observations while allowing Playwright events to arrive."""
    deadline = time.monotonic() + timeout_ms / 1_000
    while time.monotonic() < deadline:
        if predicate():
            return
        page.wait_for_timeout(100)
    raise AssertionError(f"Не выполнено ожидание за {timeout_ms} мс: {description}")
