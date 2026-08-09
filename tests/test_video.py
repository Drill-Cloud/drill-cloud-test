from __future__ import annotations

import pytest
from playwright.sync_api import Page

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import VideoPage


@pytest.mark.case("VIDEO-01")
@pytest.mark.p0
@pytest.mark.video
def test_configured_camera_is_visible(app_page: Page, test_config: TestConfig) -> None:
    """Настроенная камера имеет заголовок, video element и при строгом режиме начинает playback."""
    if not test_config.video_edge_id:
        pytest.skip("Для video smoke задайте E2E_VIDEO_EDGE_ID")

    video = VideoPage(app_page)
    video.open_edge(test_config.video_edge_id)
    video.assert_loaded(test_config.video_edge_id)
    video.assert_first_camera_visible()
    if test_config.require_video_playback:
        video.wait_for_playback(test_config.timeout_ms)


@pytest.mark.case("VIDEO-03")
@pytest.mark.p0
@pytest.mark.video
def test_edge_without_cameras_has_safe_empty_state(app_page: Page, test_config: TestConfig) -> None:
    """Буровая без камер показывает понятное пустое состояние."""
    if not test_config.no_video_edge_id:
        pytest.skip("Для проверки empty state задайте E2E_NO_VIDEO_EDGE_ID")

    video = VideoPage(app_page)
    video.open_edge(test_config.no_video_edge_id)
    video.assert_loaded(test_config.no_video_edge_id)
    video.assert_no_cameras()
