from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from .base import BasePage


class SettingsPage(BasePage):
    def open_page(self) -> None:
        self.open("/settings")

    def assert_loaded(self) -> None:
        self.assert_heading("Глобальные настройки интерфейса")
        expect(self.page.locator(".settings-message")).to_be_hidden()
        for section in ("Видеоплеер", "Live-график", "Архив и интерфейс"):
            expect(self.page.get_by_role("heading", name=section, exact=True)).to_be_visible()

    def number_field(self, label: str) -> Locator:
        accessible_name = re.compile(rf"^{re.escape(label)}(?:\s|$)")
        return self.page.get_by_role("spinbutton", name=accessible_name)

    def read_number(self, label: str) -> float:
        return float(self.number_field(label).input_value())

    def fill_number(self, label: str, value: float) -> None:
        self.number_field(label).fill(f"{value:g}")

    def save(self) -> None:
        self.page.get_by_role("button", name="Сохранить", exact=True).click()
        expect(self.page.get_by_role("dialog", name="Настройки сохранены")).to_be_visible()

    def close_saved_modal(self) -> None:
        self.page.get_by_role("button", name="Продолжить", exact=True).click()
        expect(self.page.get_by_role("dialog", name="Настройки сохранены")).to_be_hidden()

    def saved_modal(self) -> Locator:
        return self.page.get_by_role("dialog", name="Настройки сохранены")
