from __future__ import annotations

import re

from playwright.sync_api import expect

from .base import EdgeSectionPage


class EdgePage(EdgeSectionPage):
    def open_edge(self, edge_id: str) -> None:
        self.open(self.edge_path(edge_id))

    def assert_overview(self, edge_id: str) -> None:
        self.assert_edge_shell(edge_id)
        for label in ("Всего показателей", "Live", "Архив", "Последнее обновление"):
            expect(self.page.locator(".summary-card").filter(has_text=label)).to_be_visible()
        expect(self.page.locator(".current-transport")).to_have_text(re.compile(r"^(SSE live|polling)$"))

    def open_from_overview(self, section: str) -> None:
        self.page.get_by_role("button", name=section, exact=True).click()

    def back_to_list(self) -> None:
        self.page.get_by_role("button", name="К списку", exact=True).click()
