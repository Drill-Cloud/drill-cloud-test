from __future__ import annotations

import pytest
from playwright.sync_api import Page

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import VideoPage


@pytest.mark.case("VIDEO-01")
@pytest.mark.p0
@pytest.mark.video
def test_configured_camera_is_visible(app_page: Page, test_config: TestConfig, video_edge_id: str) -> None:
    """Настроенная камера имеет заголовок, video element и при строгом режиме начинает playback."""
    video = VideoPage(app_page)
    video.open_edge(video_edge_id)
    video.assert_loaded(video_edge_id)
    video.assert_first_camera_visible()
    if test_config.require_video_playback:
        video.wait_for_playback(test_config.timeout_ms)


@pytest.mark.case("VIDEO-03")
@pytest.mark.p0
@pytest.mark.video
def test_edge_without_cameras_has_safe_empty_state(app_page: Page, no_video_edge_id: str) -> None:
    """Буровая без камер показывает понятное пустое состояние."""
    video = VideoPage(app_page)
    video.open_edge(no_video_edge_id)
    video.assert_loaded(no_video_edge_id)
    video.assert_no_cameras()
