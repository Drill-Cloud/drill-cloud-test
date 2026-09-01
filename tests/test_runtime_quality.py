from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, Request, expect

from drill_cloud_test.config import TestConfig
from drill_cloud_test.diagnostics import BrowserDiagnostics
from drill_cloud_test.pages import DashboardPage, IndicatorsPage


@pytest.mark.case("UI-02-request-budget")
@pytest.mark.p2
@pytest.mark.integration
def test_current_page_does_not_create_request_storm(
    app_page: Page,
    edge_id: str,
    test_config: TestConfig,
    diagnostics: BrowserDiagnostics,
) -> None:
    """Indicators остаётся в разумном бюджете запросов и не создаёт runtime errors."""
    api_requests: list[Request] = []
    app_page.on("request", lambda request: api_requests.append(request) if "/api/current" in request.url else None)

    IndicatorsPage(app_page).open_edge(edge_id)
    app_page.wait_for_timeout(test_config.sse_observe_seconds * 1_000)

    assert len(api_requests) <= test_config.max_current_requests, (
        f"За {test_config.sse_observe_seconds} секунд выполнено {len(api_requests)} current-запросов; "
        f"лимит {test_config.max_current_requests}"
    )
    diagnostics.assert_no_runtime_errors()


@pytest.mark.case("UI-02-unknown-route")
@pytest.mark.p2
def test_unknown_spa_route_returns_to_dashboard(app_page: Page) -> None:
    """Неизвестный вложенный URL безопасно перенаправляется на dashboard."""
    app_page.goto("/definitely-unknown-e2e-route", wait_until="domcontentloaded")
    expect(app_page).to_have_url(re.compile(r"/edges/?(?:[?#].*)?$"))
    DashboardPage(app_page).assert_loaded()
