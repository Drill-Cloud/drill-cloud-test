from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.pages import DashboardPage, SettingsPage


@pytest.mark.case("SETTINGS-01")
@pytest.mark.p0
@pytest.mark.settings
@pytest.mark.serial
def test_settings_save_modal_and_persistence(app_page: Page) -> None:
    """Настройка сохраняется на backend, показывает modal и переживает reload; исходное значение восстанавливается."""
    dashboard = DashboardPage(app_page)
    dashboard.open_settings()
    settings = SettingsPage(app_page)
    settings.assert_loaded()

    field = "Период окна"
    initial = settings.read_number(field)
    changed = initial - 1 if initial >= 120 else initial + 1

    try:
        settings.fill_number(field, changed)
        settings.save()
        expect(settings.saved_modal()).to_contain_text("Новые параметры применены")
        settings.close_saved_modal()

        app_page.reload(wait_until="domcontentloaded")
        settings.assert_loaded()
        expect(settings.number_field(field)).to_have_value(f"{changed:g}")
    finally:
        if settings.saved_modal().is_visible():
            settings.close_saved_modal()
        settings.fill_number(field, initial)
        settings.save()
        settings.close_saved_modal()
