from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import IndicatorsPage


@pytest.mark.case("CURRENT-01")
@pytest.mark.p0
@pytest.mark.current
def test_current_indicators_and_search(app_page: Page, edge_id: str, test_config: TestConfig) -> None:
    """Показатели содержат имя, тег и значение; поиск работает по подготовленному признаку."""
    indicators = IndicatorsPage(app_page)
    indicators.open_edge(edge_id)
    indicators.assert_loaded(edge_id)
    expect(indicators.widgets.first).to_be_visible()

    initial_count = indicators.widgets.count()
    query = test_config.indicator_query
    if not query:
        query = indicators.widgets.first.locator(".metric-widget__id").inner_text().strip()

    indicators.search_for(query)
    expect(indicators.widgets.first).to_be_visible()
    assert 0 < indicators.widgets.count() <= initial_count
    expect(indicators.widgets.first.locator(".metric-widget__name")).not_to_be_empty()
    expect(indicators.widgets.first.locator(".metric-widget__value")).not_to_be_empty()

    indicators.clear_search()
    expect(indicators.widgets).to_have_count(initial_count)


@pytest.mark.case("CURRENT-02")
@pytest.mark.p1
@pytest.mark.current
def test_live_indicator_changes_without_reload(app_page: Page, edge_id: str, test_config: TestConfig) -> None:
    """Заранее определённый live-тег меняет значение без обновления страницы."""
    if not test_config.live_tag:
        pytest.skip("Для проверки live-изменения задайте E2E_LIVE_TAG")

    indicators = IndicatorsPage(app_page)
    indicators.open_edge(edge_id)
    indicators.assert_loaded(edge_id)
    initial = indicators.value_for_tag(test_config.live_tag)
    deadline = time.monotonic() + test_config.live_wait_seconds

    while time.monotonic() < deadline:
        app_page.wait_for_timeout(1_000)
        if indicators.value_for_tag(test_config.live_tag) != initial:
            return

    pytest.fail(f"Значение {test_config.live_tag!r} не изменилось за {test_config.live_wait_seconds} секунд: {initial}")


@pytest.mark.case("CURRENT-03")
@pytest.mark.p0
@pytest.mark.current
def test_live_chart_is_rendered(app_page: Page, edge_id: str) -> None:
    """Live-график доходит до canvas либо корректного состояния отсутствия числовых данных."""
    indicators = IndicatorsPage(app_page)
    indicators.open_edge(edge_id)
    indicators.assert_loaded(edge_id)

    canvas = app_page.locator(".current-live-chart__canvas canvas").first
    empty = app_page.get_by_text("Нет числовых показателей для графика", exact=True)
    expect(canvas.or_(empty)).to_be_visible()
