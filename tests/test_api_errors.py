from __future__ import annotations

import pytest
from playwright.sync_api import Page, Route, expect

from drill_cloud_test.pages import IndicatorsPage, SettingsPage, VideoPage


def _server_error(route: Route) -> None:
    route.fulfill(status=500, content_type="application/json", body='{"message":"Synthetic E2E failure"}')


@pytest.mark.case("EDGE-04")
@pytest.mark.p2
@pytest.mark.edges
def test_dashboard_handles_edge_api_failure(app_page: Page) -> None:
    """Dashboard показывает безопасное сообщение при HTTP 500 списка буровых."""
    app_page.route("**/api/edge*", _server_error)
    app_page.reload(wait_until="domcontentloaded")
    expect(app_page.get_by_text("Не удалось загрузить список установок", exact=False)).to_be_visible()
    expect(app_page.get_by_role("heading", name="Установки", exact=True)).to_be_visible()


@pytest.mark.case("CURRENT-error")
@pytest.mark.p2
@pytest.mark.current
def test_indicators_handle_current_api_failure(app_page: Page, edge_id: str) -> None:
    """Current-раздел не падает и объясняет ошибку backend."""

    def fail_current(route: Route) -> None:
        if "/api/current?" in route.request.url and "/events" not in route.request.url:
            _server_error(route)
        else:
            route.continue_()

    app_page.route("**/api/current**", fail_current)
    IndicatorsPage(app_page).open_edge(edge_id)
    expect(app_page.get_by_text("Не удалось загрузить текущие значения", exact=False)).to_be_visible()


@pytest.mark.case("VIDEO-error")
@pytest.mark.p2
@pytest.mark.video
def test_video_handles_camera_api_failure(app_page: Page, edge_id: str) -> None:
    """Видео-раздел остаётся доступным при HTTP 500 camera endpoint."""
    app_page.route("**/api/camera*", _server_error)
    VideoPage(app_page).open_edge(edge_id)
    expect(app_page.get_by_text("Не удалось загрузить камеры", exact=False)).to_be_visible()


@pytest.mark.case("SETTINGS-03-error")
@pytest.mark.p2
@pytest.mark.settings
def test_settings_do_not_show_success_after_failed_save(app_page: Page) -> None:
    """Ошибка PUT ui-settings видна пользователю и не создаёт ложный success modal."""
    settings = SettingsPage(app_page)
    settings.open_page()
    settings.assert_loaded()

    def fail_settings_put(route: Route) -> None:
        if route.request.method == "PUT":
            _server_error(route)
        else:
            route.continue_()

    app_page.route("**/api/me/ui-settings", fail_settings_put)
    settings.fill_number("Период окна", 26)
    settings.click_save()

    expect(app_page.locator(".settings-message--warning")).to_be_visible()
    expect(settings.saved_modal()).to_be_hidden()
