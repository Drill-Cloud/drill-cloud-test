from __future__ import annotations

import pytest
from playwright.sync_api import Playwright

from drill_cloud_test.config import TestConfig


@pytest.mark.case("ENV-01")
@pytest.mark.p0
@pytest.mark.api
def test_cloud_health(playwright: Playwright, test_config: TestConfig) -> None:
    """Cloud API отвечает и возвращает JSON-состояние сервисов."""
    request = playwright.request.new_context(ignore_https_errors=False)
    try:
        response = request.get(test_config.health_url)
        assert response.ok, f"GET {test_config.health_url}: {response.status} {response.text()}"
        payload = response.json()
        assert isinstance(payload, dict), f"Ожидался JSON object, получено: {payload!r}"
    finally:
        request.dispose()
