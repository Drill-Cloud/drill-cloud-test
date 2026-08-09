from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.diagnostics import BrowserDiagnostics
from drill_cloud_test.pages import DashboardPage, EdgePage


@pytest.mark.case("EDGE-01")
@pytest.mark.p0
@pytest.mark.edges
def test_dashboard_list_and_refresh(app_page: Page, diagnostics: BrowserDiagnostics) -> None:
    """Список, статистика и ручное обновление работают без дублей и runtime-ошибок."""
    dashboard = DashboardPage(app_page)
    dashboard.assert_loaded()
    assert dashboard.statistic("Всего установок") == dashboard.cards.count()
    assert dashboard.statistic("Найдено") == dashboard.cards.count()

    before = dashboard.cards.count()
    dashboard.refresh()
    expect(dashboard.cards).to_have_count(before)
    diagnostics.assert_no_runtime_errors()


@pytest.mark.case("EDGE-02")
@pytest.mark.p0
@pytest.mark.edges
def test_dashboard_search_by_edge_id(app_page: Page, edge_id: str) -> None:
    """Поиск находит ID, показывает empty state и восстанавливает список."""
    dashboard = DashboardPage(app_page)
    initial_count = dashboard.cards.count()

    dashboard.search_for(edge_id)
    expect(dashboard.card(edge_id)).to_have_count(1)
    assert dashboard.statistic("Найдено") == dashboard.cards.count()
    assert 0 < dashboard.cards.count() <= initial_count

    dashboard.search_for("__drill_cloud_no_such_edge__")
    expect(dashboard.cards).to_have_count(0)
    expect(app_page.get_by_text("В cloud-v3 пока нет буровых", exact=True)).to_be_visible()

    dashboard.clear_search()
    expect(dashboard.cards).to_have_count(initial_count)


@pytest.mark.case("EDGE-03")
@pytest.mark.p0
@pytest.mark.edges
def test_open_edge_and_return_to_list(app_page: Page, edge_id: str) -> None:
    """Карточка открывает правильную буровую, а верхняя панель возвращает к списку."""
    dashboard = DashboardPage(app_page)
    dashboard.open_edge(edge_id)

    edge = EdgePage(app_page)
    edge.assert_overview(edge_id)
    edge.back_to_list()
    dashboard.assert_loaded()
