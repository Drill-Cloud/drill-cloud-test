from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base import EdgeSectionPage


class VideoPage(EdgeSectionPage):
    @property
    def cameras(self) -> Locator:
        return self.page.get_by_test_id("camera-view")

    def open_edge(self, edge_id: str) -> None:
        self.open(self.edge_path(edge_id, "/video"))

    def assert_loaded(self, edge_id: str) -> None:
        self.assert_edge_shell(edge_id)
        expect(self.page.get_by_role("heading", name="Видеопотоки буровой")).to_be_visible()

    def assert_no_cameras(self) -> None:
        expect(self.page.get_by_text("Камеры для этой буровой не настроены", exact=True)).to_be_visible()

    def assert_first_camera_visible(self) -> Locator:
        camera = self.cameras.first
        expect(camera).to_be_visible()
        expect(camera.get_by_test_id("camera-video")).to_be_visible()
        expect(camera.locator(".camera-view__caption strong")).not_to_be_empty()
        return camera

    def wait_for_playback(self, timeout_ms: int) -> None:
        video = self.cameras.first.get_by_test_id("camera-video")
        video.wait_for(state="visible")
        self.page.wait_for_function(
            "element => !element.paused && element.readyState >= 2 && element.currentTime > 0",
            arg=video.element_handle(),
            timeout=timeout_ms,
        )
