from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from .base import EdgeSectionPage


class ArchivePage(EdgeSectionPage):
    @property
    def panels(self) -> Locator:
        return self.page.get_by_test_id("history-chart-panel")

    def open_edge(self, edge_id: str) -> None:
        self.open(self.edge_path(edge_id, "/archive"))

    def assert_loaded(self, edge_id: str) -> None:
        self.assert_edge_shell(edge_id)
        expect(self.page.get_by_role("heading", name="График параметров")).to_be_visible()
        expect(self.page.get_by_role("button", name="24 часа", exact=True)).to_be_visible()
        expect(self.panels).to_have_count(1)

    def choose_period(self, label: str) -> None:
        self.page.get_by_role("button", name=label, exact=True).click()

    def open_picker(self, panel: Locator | None = None) -> Locator:
        target = panel or self.panels.first
        target.get_by_role("button", name="Показать выбор показателей").click()
        dropdown = target.get_by_test_id("history-tag-picker-dropdown")
        expect(dropdown).to_be_visible()
        return dropdown

    def select_tag(self, query: str | None = None, panel: Locator | None = None) -> str:
        target = panel or self.panels.first
        dropdown = self.open_picker(target)
        search = target.locator(".history-tag-picker__chips input")
        if query:
            search.fill(query)
        option = dropdown.get_by_role("option").first
        expect(option).to_be_visible()
        selected_text = option.inner_text().strip()
        option.click()
        return selected_text

    def assert_chart_terminal_state(self, *, require_data: bool) -> None:
        data = self.page.get_by_test_id("history-chart").first
        empty = self.page.get_by_text(re.compile(r"Нет данных для выбранного диапазона"), exact=True).first
        expect(data.or_(empty)).to_be_visible()
        if require_data:
            expect(data).to_be_visible()

    def add_chart(self) -> None:
        self.page.get_by_role("button", name="Добавить график", exact=True).click()

    def remove_last_chart(self) -> None:
        self.panels.last.get_by_role("button", name="Удалить график").click()
