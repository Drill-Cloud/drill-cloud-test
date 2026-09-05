from __future__ import annotations

import json
import time
from copy import deepcopy
from datetime import UTC, datetime

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.api import DrillCloudApi
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
def test_live_indicator_changes_without_reload(
    app_page: Page,
    edge_id: str,
    test_config: TestConfig,
    api_client: DrillCloudApi,
) -> None:
    """Live-тег меняется без reload; без publisher используется безопасный SSE-стаб."""
    live_tag = test_config.live_tag
    if not live_tag:
        current = api_client.get_current(edge_id)
        items = current.get("items", [])
        assert isinstance(items, list) and items, f"Для {edge_id!r} нет current-данных"
        source = next((item for item in items if isinstance(item.get("value"), (int, float))), items[0])
        live_tag = str(source["tag"])
        first = deepcopy(current)
        second = deepcopy(current)
        now = datetime.now(UTC).isoformat()
        base_value = float(source.get("value") or 0)
        for snapshot, value in ((first, base_value + 1), (second, base_value + 2)):
            item = next(candidate for candidate in snapshot["items"] if candidate.get("tag") == live_tag)
            item["value"] = value
            item["updatedAt"] = now
            item["time"] = now

        snapshots_json = json.dumps([first, second], ensure_ascii=False)
        app_page.add_init_script(
            script=f"""
            (() => {{
              const snapshots = {snapshots_json};
              class SyntheticEventSource {{
                constructor(url) {{
                  this.url = String(url);
                  this.readyState = 0;
                  this.onopen = null;
                  this.onerror = null;
                  this.onmessage = null;
                  this.index = 0;
                  this.openTimer = setTimeout(() => {{
                    this.readyState = 1;
                    this.onopen?.({{ type: 'open' }});
                  }}, 20);
                  this.timer = setInterval(() => {{
                    const data = JSON.stringify(snapshots[this.index % snapshots.length]);
                    this.index += 1;
                    this.onmessage?.({{ type: 'message', data }});
                  }}, 400);
                }}
                close() {{
                  clearTimeout(this.openTimer);
                  clearInterval(this.timer);
                  this.readyState = 2;
                }}
                addEventListener(type, listener) {{ this[`on${{type}}`] = listener; }}
                removeEventListener(type, listener) {{
                  if (this[`on${{type}}`] === listener) this[`on${{type}}`] = null;
                }}
              }}
              SyntheticEventSource.CONNECTING = 0;
              SyntheticEventSource.OPEN = 1;
              SyntheticEventSource.CLOSED = 2;
              Object.defineProperty(window, 'EventSource', {{
                configurable: true,
                writable: true,
                value: SyntheticEventSource,
              }});
            }})()
            """
        )

    indicators = IndicatorsPage(app_page)
    indicators.open_edge(edge_id)
    indicators.assert_loaded(edge_id)
    initial = indicators.value_for_tag(live_tag)
    deadline = time.monotonic() + test_config.live_wait_seconds

    while time.monotonic() < deadline:
        app_page.wait_for_timeout(1_000)
        if indicators.value_for_tag(live_tag) != initial:
            return

    pytest.fail(f"Значение {live_tag!r} не изменилось за {test_config.live_wait_seconds} секунд: {initial}")


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
