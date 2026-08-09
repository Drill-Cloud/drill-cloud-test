from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from .base import BasePage


class DashboardPage(BasePage):
    @property
    def cards(self) -> Locator:
        return self.page.locator(".edge-card")

    @property
    def search(self) -> Locator:
        return self.page.get_by_placeholder("Поиск буровой")

    def assert_loaded(self) -> None:
        self.assert_heading("Буровые установки")
        expect(self.page.get_by_label("Статистика буровых")).to_be_visible()
        expect(self.page.get_by_label("Буровые установки")).to_be_visible()

    def card(self, edge_id: str) -> Locator:
        exact_id = self.page.locator(".edge-card__title span").filter(has_text=re.compile(rf"^{re.escape(edge_id)}$"))
        return self.cards.filter(has=exact_id)

    def discover_edge_id(self) -> str:
        expect(self.cards.first).to_be_visible()
        return self.cards.first.locator(".edge-card__title span").inner_text().strip()

    def open_edge(self, edge_id: str) -> None:
        card = self.card(edge_id)
        expect(card).to_have_count(1)
        card.get_by_role("button", name="Подробнее", exact=True).click()

    def search_for(self, query: str) -> None:
        self.search.fill(query)

    def clear_search(self) -> None:
        self.search.fill("")

    def statistic(self, label: str) -> int:
        block = self.page.locator(".dashboard-stat").filter(has_text=label)
        return int(block.locator("strong").inner_text())

    def refresh(self) -> None:
        self.page.get_by_title("Обновить список").click()

    def open_settings(self) -> None:
        self.page.get_by_role("button", name="Настройки", exact=True).click()
