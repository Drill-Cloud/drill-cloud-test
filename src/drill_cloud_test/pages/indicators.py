from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base import EdgeSectionPage


class IndicatorsPage(EdgeSectionPage):
    @property
    def widgets(self) -> Locator:
        return self.page.get_by_test_id("metric-widget")

    def open_edge(self, edge_id: str) -> None:
        self.open(self.edge_path(edge_id, "/indicators"))

    def assert_loaded(self, edge_id: str) -> None:
        self.assert_edge_shell(edge_id)
        expect(self.page.get_by_role("heading", name="Текущие значения")).to_be_visible()
        expect(self.page.get_by_role("heading", name="Живой график текущих значений")).to_be_visible()

    def search_for(self, query: str) -> None:
        self.page.get_by_placeholder("Поиск показателя").fill(query)

    def clear_search(self) -> None:
        self.page.get_by_placeholder("Поиск показателя").fill("")

    def widget_for_tag(self, tag: str) -> Locator:
        return self.page.locator(f'[data-testid="metric-widget"][data-tag="{tag}"]')

    def value_for_tag(self, tag: str) -> str:
        widget = self.widget_for_tag(tag)
        expect(widget).to_be_visible()
        return widget.locator(".metric-widget__value").inner_text().strip()
