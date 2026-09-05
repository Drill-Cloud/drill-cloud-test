from __future__ import annotations

from copy import deepcopy

import pytest
from playwright.sync_api import Page, Request, Route, expect

from drill_cloud_test.api import DrillCloudApi
from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import ArchivePage, EdgePage, IndicatorsPage
from drill_cloud_test.ui_settings import default_ui_settings
from drill_cloud_test.waits import wait_until


def _is_sse(request: Request) -> bool:
    return "/api/current/events?" in request.url


def _is_current_poll(request: Request) -> bool:
    return "/api/current?" in request.url and "/events" not in request.url


@pytest.mark.case("CURRENT-02-SSE")
@pytest.mark.p1
@pytest.mark.current
@pytest.mark.integration
def test_navigation_creates_one_sse_connection_per_live_section(app_page: Page, edge_id: str) -> None:
    """Indicators и Archive создают по одному SSE, не накапливая соединения при навигации."""
    sse_requests: list[Request] = []
    app_page.on("request", lambda request: sse_requests.append(request) if _is_sse(request) else None)

    IndicatorsPage(app_page).open_edge(edge_id)
    wait_until(app_page, lambda: len(sse_requests) == 1, timeout_ms=10_000, description="первый SSE indicators")
    expect(app_page.get_by_test_id("current-transport")).to_have_attribute("data-transport", "sse")

    ArchivePage(app_page).open_edge(edge_id)
    wait_until(app_page, lambda: len(sse_requests) == 2, timeout_ms=10_000, description="новый SSE archive")
    expect(app_page.get_by_test_id("current-transport")).to_have_attribute("data-transport", "sse")
    assert len(sse_requests) == 2

    EdgePage(app_page).navigate("Видео")
    app_page.wait_for_timeout(500)
    assert len(sse_requests) == 2, "Видео-раздел не должен создавать current SSE"


@pytest.mark.case("CURRENT-02-fallback")
@pytest.mark.p1
@pytest.mark.current
@pytest.mark.integration
@pytest.mark.serial
def test_polling_takes_over_when_sse_is_unavailable(
    app_page: Page,
    edge_id: str,
    api_client: DrillCloudApi,
    test_config: TestConfig,
) -> None:
    """При обрыве EventSource UI переключается на контролируемый fallback polling."""
    original_response = api_client.get_ui_settings()
    original_settings = original_response.get("settings")
    temporary_settings = deepcopy(original_settings or default_ui_settings())
    temporary_settings["liveChart"]["fallbackPollingMs"] = 1_000
    polls: list[Request] = []

    try:
        api_client.save_ui_settings(temporary_settings)
        app_page.reload(wait_until="domcontentloaded")
        app_page.on("request", lambda request: polls.append(request) if _is_current_poll(request) else None)

        def abort_sse(route: Route) -> None:
            route.abort("connectionrefused")

        app_page.route("**/api/current/events?*", abort_sse)
        IndicatorsPage(app_page).open_edge(edge_id)

        expect(app_page.get_by_test_id("current-transport")).to_have_attribute("data-transport", "polling")
        wait_until(
            app_page,
            lambda: len(polls) >= 2,
            timeout_ms=test_config.sse_observe_seconds * 1_000,
            description="минимум два current polling запроса",
        )
    finally:
        if original_settings is None:
            api_client.delete_ui_settings()
        else:
            api_client.save_ui_settings(original_settings)
