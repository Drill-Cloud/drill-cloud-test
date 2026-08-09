from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.pages import EdgePage


@pytest.mark.case("OVERVIEW-01")
@pytest.mark.p0
@pytest.mark.edges
def test_edge_overview_summary(app_page: Page, edge_id: str) -> None:
    """Обзор показывает идентичность буровой, сводку и состояние транспорта current."""
    overview = EdgePage(app_page)
    overview.open_edge(edge_id)
    overview.assert_overview(edge_id)
    expect(app_page.locator(".summary-card strong").first).not_to_be_empty()


@pytest.mark.case("OVERVIEW-02")
@pytest.mark.p0
@pytest.mark.edges
def test_edge_navigation_routes(app_page: Page, edge_id: str) -> None:
    """Все основные разделы доступны из боковой навигации и сохраняют edge ID."""
    overview = EdgePage(app_page)
    overview.open_edge(edge_id)

    routes = {
        "Показатели": "/indicators",
        "Архив": "/archive",
        "Видео": "/video",
        "Обзор": "",
    }
    for section, suffix in routes.items():
        overview.navigate(section)
        expect(app_page).to_have_url(overview.edge_path(edge_id, suffix))
