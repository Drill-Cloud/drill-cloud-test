from __future__ import annotations

import re
from urllib.parse import quote

from playwright.sync_api import Page, expect


class BasePage:
    """Общие операции страниц Drill Cloud."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str = "/") -> None:
        self.page.goto(path, wait_until="domcontentloaded")

    def assert_heading(self, name: str) -> None:
        expect(self.page.get_by_role("heading", name=name, exact=True)).to_be_visible()

    @staticmethod
    def edge_path(edge_id: str, suffix: str = "") -> str:
        encoded = quote(edge_id, safe="")
        return f"/edges/{encoded}{suffix}"


class EdgeSectionPage(BasePage):
    def assert_edge_shell(self, edge_id: str) -> None:
        edge_path = re.escape(self.edge_path(edge_id))
        expect(self.page).to_have_url(re.compile(rf"{edge_path}(?:/[^?#]*)?(?:[?#].*)?$"))
        expect(self.page.get_by_role("heading", level=1)).to_be_visible()
        expect(self.page.get_by_role("navigation", name="Основная навигация")).to_be_visible()

    def navigate(self, section: str) -> None:
        self.page.get_by_role("navigation", name="Основная навигация").get_by_role(
            "button", name=section, exact=True
        ).click()

    def refresh(self) -> None:
        self.page.get_by_title("Обновить данные").click()
