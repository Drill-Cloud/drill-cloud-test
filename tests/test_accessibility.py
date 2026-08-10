from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.accessibility import assert_basic_accessibility, assert_no_horizontal_overflow
from drill_cloud_test.pages import ArchivePage, DashboardPage, SettingsPage


@pytest.mark.case("UI-01-accessibility")
@pytest.mark.p2
@pytest.mark.accessibility
def test_dashboard_and_settings_have_basic_accessibility(app_page: Page) -> None:
    """Основные страницы не содержат duplicate IDs, безымянных кнопок и img без alt."""
    DashboardPage(app_page).assert_loaded()
    assert_basic_accessibility(app_page)

    SettingsPage(app_page).open_page()
    SettingsPage(app_page).assert_loaded()
    assert_basic_accessibility(app_page)


@pytest.mark.case("UI-01-responsive")
@pytest.mark.p2
@pytest.mark.accessibility
@pytest.mark.parametrize("width,height", [(1024, 768), (1280, 800), (1440, 1000), (1920, 1080)])
def test_critical_pages_do_not_overflow_viewport(app_page: Page, edge_id: str, width: int, height: int) -> None:
    """Dashboard, Settings и раскрытый archive picker не выходят за ширину поддерживаемых viewport."""
    app_page.set_viewport_size({"width": width, "height": height})
    DashboardPage(app_page).assert_loaded()
    assert_no_horizontal_overflow(app_page)

    SettingsPage(app_page).open_page()
    SettingsPage(app_page).assert_loaded()
    assert_no_horizontal_overflow(app_page)

    archive = ArchivePage(app_page)
    archive.open_edge(edge_id)
    archive.assert_loaded(edge_id)
    archive.open_picker()
    assert_no_horizontal_overflow(app_page)
    expect(archive.panels.first).to_be_visible()
