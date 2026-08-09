from __future__ import annotations

import pytest
from playwright.sync_api import Browser, Page, expect

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import DashboardPage, EdgePage
from drill_cloud_test.pages.login import ensure_authenticated


@pytest.mark.case("AUTH-01")
@pytest.mark.p0
@pytest.mark.auth
def test_authenticated_session_survives_reload(app_page: Page, edge_id: str) -> None:
    """Пользователь видит dashboard, сохраняет сессию и открывает прямой URL буровой."""
    DashboardPage(app_page).assert_loaded()
    app_page.reload(wait_until="domcontentloaded")
    DashboardPage(app_page).assert_loaded()

    edge = EdgePage(app_page)
    edge.open_edge(edge_id)
    edge.assert_overview(edge_id)


@pytest.mark.case("AUTH-04")
@pytest.mark.p0
@pytest.mark.auth
@pytest.mark.serial
def test_logout_hides_protected_ui(browser: Browser, test_config: TestConfig) -> None:
    """Выход завершает UI-сессию и возвращает пользователя в Keycloak."""
    context = browser.new_context(base_url=test_config.base_url, locale="ru-RU")
    try:
        page = context.new_page()
        page.set_default_timeout(test_config.timeout_ms)
        ensure_authenticated(page, test_config)
        logout = page.get_by_role("button", name="Выйти", exact=True)
        if logout.count() == 0:
            pytest.skip("SSO отключён на выбранном окружении")

        logout.click()
        expect(page.locator("#username, input[name='username']").first).to_be_visible(timeout=test_config.timeout_ms)
        expect(page.get_by_role("heading", name="Буровые установки", exact=True)).to_be_hidden()
    finally:
        context.close()
