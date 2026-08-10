from __future__ import annotations

import pytest
from playwright.sync_api import Browser

from drill_cloud_test.diagnostics import BrowserDiagnostics


@pytest.mark.unit
def test_playwright_can_register_diagnostic_handlers(browser: Browser) -> None:
    """Playwright can attach its wrappers to BrowserDiagnostics bound methods."""
    diagnostics = BrowserDiagnostics()
    context = browser.new_context()
    try:
        page = context.new_page()
        page.on("console", diagnostics.on_console)
        page.on("pageerror", diagnostics.on_page_error)
        page.on("requestfailed", diagnostics.on_request_failed)
        page.set_content("<script>console.error('diagnostic probe')</script>")
        assert diagnostics.console_errors == ["console: diagnostic probe"]
    finally:
        context.close()
