from __future__ import annotations

import pytest
from playwright.sync_api import Page, WebSocket, expect

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import EdgePage, VideoPage
from drill_cloud_test.waits import wait_until


@pytest.mark.case("VIDEO-02-connections")
@pytest.mark.p1
@pytest.mark.video
@pytest.mark.integration
def test_video_websockets_are_closed_and_recreated_once(
    app_page: Page, test_config: TestConfig, video_edge_id: str
) -> None:
    """Уход с Video закрывает camera WebSocket, возврат создаёт по одному новому соединению."""
    sockets: list[WebSocket] = []
    closed_urls: list[str] = []

    def observe_socket(socket: WebSocket) -> None:
        sockets.append(socket)
        socket.on("close", lambda closed_socket: closed_urls.append(closed_socket.url))

    app_page.on("websocket", observe_socket)
    video = VideoPage(app_page)
    video.open_edge(video_edge_id)
    expect(video.cameras.first).to_be_visible()
    camera_count = video.cameras.count()
    wait_until(
        app_page,
        lambda: len(sockets) == camera_count,
        timeout_ms=test_config.timeout_ms,
        description="по одному WebSocket на камеру",
    )

    EdgePage(app_page).navigate("Обзор")
    wait_until(
        app_page,
        lambda: len(closed_urls) == camera_count,
        timeout_ms=test_config.timeout_ms,
        description="закрытие WebSocket после ухода с Video",
    )

    EdgePage(app_page).navigate("Видео")
    wait_until(
        app_page,
        lambda: len(sockets) == camera_count * 2,
        timeout_ms=test_config.timeout_ms,
        description="ровно одно новое соединение на камеру",
    )
    assert len(sockets) == camera_count * 2
