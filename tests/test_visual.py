from __future__ import annotations

import pytest
from playwright.sync_api import Page

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import DashboardPage, SettingsPage
from drill_cloud_test.visual import assert_visual_snapshot


@pytest.mark.case("UI-01-visual")
@pytest.mark.p2
@pytest.mark.visual
def test_dashboard_visual_baseline(app_page: Page, test_config: TestConfig, browser_name: str) -> None:
    """Dashboard layout matches an explicitly approved screenshot baseline."""
    if not test_config.visual_enabled:
        pytest.skip("Для visual regression задайте E2E_VISUAL_ENABLED=true")
    DashboardPage(app_page).assert_loaded()
    assert_visual_snapshot(
        app_page,
        name="dashboard.png",
        browser_name=browser_name,
        update=test_config.update_snapshots,
        mask=[app_page.get_by_test_id("edge-card"), app_page.locator(".dashboard-stat strong")],
    )


@pytest.mark.case("UI-01-visual-settings")
@pytest.mark.p2
@pytest.mark.visual
def test_settings_visual_baseline(app_page: Page, test_config: TestConfig, browser_name: str) -> None:
    """Settings layout matches an explicitly approved screenshot baseline."""
    if not test_config.visual_enabled:
        pytest.skip("Для visual regression задайте E2E_VISUAL_ENABLED=true")
    settings = SettingsPage(app_page)
    settings.open_page()
    settings.assert_loaded()
    assert_visual_snapshot(
        app_page,
        name="settings.png",
        browser_name=browser_name,
        update=test_config.update_snapshots,
        mask=[app_page.locator(".settings-field input, .settings-field select")],
    )
