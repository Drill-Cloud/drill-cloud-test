from __future__ import annotations

from typing import ClassVar

from playwright.sync_api import Locator, expect

from .base import BasePage


class SettingsPage(BasePage):
    FIELD_TEST_IDS: ClassVar[dict[str, str]] = {
        "Максимальное отставание": "settings-player-max-latency",
        "Остаток буфера": "settings-player-min-remain",
        "Начальный stash": "settings-player-stash-kb",
        "Начало очистки истории": "settings-player-cleanup-max",
        "Оставлять истории": "settings-player-cleanup-min",
        "Период окна": "settings-live-window",
        "Сдвиг окна": "settings-live-shift",
        "Fallback polling": "settings-live-polling",
        "Максимум точек": "settings-live-max-points",
        "Период архива": "settings-archive-period",
    }

    def open_page(self) -> None:
        self.open("/settings")

    def assert_loaded(self) -> None:
        self.assert_heading("Глобальные настройки интерфейса")
        expect(self.page.locator(".settings-message")).to_be_hidden()
        for section in ("Видеоплеер", "Live-график", "Архив и интерфейс"):
            expect(self.page.get_by_role("heading", name=section, exact=True)).to_be_visible()

    def number_field(self, label: str) -> Locator:
        try:
            test_id = self.FIELD_TEST_IDS[label]
        except KeyError as error:
            raise ValueError(f"Неизвестное числовое поле настроек: {label}") from error
        return self.page.get_by_test_id(test_id)

    def read_number(self, label: str) -> float:
        return float(self.number_field(label).input_value())

    def fill_number(self, label: str, value: float) -> None:
        self.number_field(label).fill(f"{value:g}")

    def save(self) -> None:
        self.click_save()
        expect(self.page.get_by_role("dialog", name="Настройки сохранены")).to_be_visible()

    def click_save(self) -> None:
        self.page.get_by_test_id("settings-save").click()

    def close_saved_modal(self) -> None:
        self.page.get_by_role("button", name="Продолжить", exact=True).click()
        expect(self.page.get_by_role("dialog", name="Настройки сохранены")).to_be_hidden()

    def saved_modal(self) -> Locator:
        return self.page.get_by_role("dialog", name="Настройки сохранены")
