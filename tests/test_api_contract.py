from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from drill_cloud_test.api import DrillCloudApi
from drill_cloud_test.config import TestConfig


def _assert_keys(value: object, required: set[str], label: str) -> dict[str, object]:
    assert isinstance(value, dict), f"{label}: ожидался object"
    missing = required.difference(value)
    assert not missing, f"{label}: отсутствуют поля {sorted(missing)}"
    return value


@pytest.mark.case("API-edge/current")
@pytest.mark.p0
@pytest.mark.api
def test_edge_and_current_contract(api_client: DrillCloudApi, edge_id: str) -> None:
    """Основные DTO edge/current сохраняют обязательные поля и типы коллекций."""
    edges = _assert_keys(api_client.get_edges(), {"items"}, "edge response")
    assert isinstance(edges["items"], list)
    for index, item in enumerate(edges["items"]):
        _assert_keys(item, {"id", "name", "parentId"}, f"edge.items[{index}]")

    current = _assert_keys(api_client.get_current(edge_id), {"edge", "items"}, "current response")
    assert current["edge"] == edge_id
    assert isinstance(current["items"], list)
    for index, item in enumerate(current["items"]):
        _assert_keys(
            item,
            {"edge", "tag", "value", "createdAt", "updatedAt", "name", "unitOfMeasurement"},
            f"current.items[{index}]",
        )


@pytest.mark.case("API-settings")
@pytest.mark.p0
@pytest.mark.api
def test_ui_settings_contract(api_client: DrillCloudApi) -> None:
    """Пользовательские настройки возвращают settings и updatedAt без раскрытия чужих данных."""
    response = _assert_keys(api_client.get_ui_settings(), {"settings", "updatedAt"}, "settings response")
    settings = response["settings"]
    if settings is not None:
        _assert_keys(settings, {"version", "player", "liveChart", "archiveChart", "interface"}, "settings")


@pytest.mark.case("API-history")
@pytest.mark.p1
@pytest.mark.api
def test_history_contract(api_client: DrillCloudApi, edge_id: str, test_config: TestConfig) -> None:
    """History endpoint возвращает строки с агрегатами за подготовленный диапазон."""
    current_items = api_client.get_current(edge_id)["items"]
    assert isinstance(current_items, list) and current_items, f"Для {edge_id!r} нет current-данных"
    query = (test_config.history_tag_query or str(current_items[0].get("tag", ""))).lower()
    matching = [
        item
        for item in current_items
        if query in str(item.get("tag", "")).lower() or query in str(item.get("name", "")).lower()
    ]
    assert matching, f"Не найден history-тег по запросу {query!r}"

    to_time = datetime.now(UTC)
    response = api_client.get_history(
        edge_id,
        str(matching[0]["tag"]),
        (to_time - timedelta(hours=24)).isoformat(),
        to_time.isoformat(),
    )
    rows = _assert_keys(response, {"rows"}, "history response")["rows"]
    assert isinstance(rows, list)
    for index, row in enumerate(rows):
        _assert_keys(row, {"time", "min_value", "avg_value", "max_value", "point_count"}, f"rows[{index}]")


@pytest.mark.case("API-camera")
@pytest.mark.p1
@pytest.mark.api
def test_camera_contract(api_client: DrillCloudApi, video_edge_id: str) -> None:
    """Camera endpoint сохраняет контракт имени, протокола и источника."""
    response = _assert_keys(api_client.get_cameras(video_edge_id), {"edge", "items"}, "camera response")
    assert response["edge"] == video_edge_id
    assert isinstance(response["items"], list)
    for index, camera in enumerate(response["items"]):
        _assert_keys(camera, {"name", "protocol", "source"}, f"camera.items[{index}]")
