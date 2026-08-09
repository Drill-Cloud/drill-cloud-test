from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import ArchivePage


@pytest.mark.case("HISTORY-01/HISTORY-02")
@pytest.mark.p0
@pytest.mark.history
def test_archive_select_tag_and_build_chart(app_page: Page, edge_id: str, test_config: TestConfig) -> None:
    """Архив открывается на 24 часах, выбирает показатель и строит однозначное состояние графика."""
    archive = ArchivePage(app_page)
    archive.open_edge(edge_id)
    archive.assert_loaded(edge_id)
    archive.select_tag(test_config.history_tag_query)
    archive.assert_chart_terminal_state(require_data=test_config.require_history_data)


@pytest.mark.case("HISTORY-03")
@pytest.mark.p0
@pytest.mark.history
def test_archive_period_presets(app_page: Page, edge_id: str) -> None:
    """Пресеты периода переключаются и обновляют активное состояние."""
    archive = ArchivePage(app_page)
    archive.open_edge(edge_id)
    archive.assert_loaded(edge_id)

    one_hour = app_page.get_by_role("button", name="1 час", exact=True)
    archive.choose_period("1 час")
    expect(one_hour).to_have_class("segmented__button--active")
    expect(app_page.locator(".source-chip")).not_to_contain_text("ожидание")


@pytest.mark.case("HISTORY-06")
@pytest.mark.p1
@pytest.mark.history
def test_multiple_archive_charts_can_be_added_and_removed(app_page: Page, edge_id: str) -> None:
    """Дополнительный график независим и удаляется без возможности удалить последний."""
    archive = ArchivePage(app_page)
    archive.open_edge(edge_id)
    archive.assert_loaded(edge_id)

    archive.add_chart()
    expect(archive.panels).to_have_count(2)
    expect(app_page.get_by_role("button", name="Удалить график")).to_have_count(2)

    archive.remove_last_chart()
    expect(archive.panels).to_have_count(1)
    expect(app_page.get_by_role("button", name="Удалить график")).to_have_count(0)
