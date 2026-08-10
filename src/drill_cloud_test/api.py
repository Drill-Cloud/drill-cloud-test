from __future__ import annotations

from typing import Any
from urllib.parse import quote

from playwright.sync_api import APIRequestContext, APIResponse, Page, Playwright

JsonObject = dict[str, Any]


class ApiError(AssertionError):
    """Raised when Drill Cloud returns an unexpected HTTP response."""


class DrillCloudApi:
    """Small typed-by-behaviour client used by fixtures and contract tests."""

    def __init__(self, request: APIRequestContext) -> None:
        self._request = request

    def close(self) -> None:
        self._request.dispose()

    def get_edges(self) -> JsonObject:
        return self._json("GET", "edge")

    def get_current(self, edge_id: str) -> JsonObject:
        return self._json("GET", f"current?edge={quote(edge_id)}")

    def get_cameras(self, edge_id: str) -> JsonObject:
        return self._json("GET", f"camera?edge={quote(edge_id)}")

    def get_history(self, edge_id: str, tag: str, from_iso: str, to_iso: str) -> JsonObject:
        query = (
            f"edge={quote(edge_id)}&tag={quote(tag)}&from={quote(from_iso)}"
            f"&to={quote(to_iso)}&granulate={quote('5 minutes')}"
        )
        return self._json("GET", f"history?{query}")

    def get_ui_settings(self) -> JsonObject:
        return self._json("GET", "me/ui-settings")

    def save_ui_settings(self, settings: JsonObject) -> JsonObject:
        return self._json("PUT", "me/ui-settings", data=settings)

    def delete_ui_settings(self) -> JsonObject:
        return self._json("DELETE", "me/ui-settings")

    def get_current_status(self, edge_id: str) -> int:
        response = self._request.get(f"current?edge={quote(edge_id)}")
        return response.status

    def _json(self, method: str, path: str, *, data: JsonObject | None = None) -> JsonObject:
        response = self._request.fetch(path, method=method, data=data)
        self._assert_ok(response, method, path)
        payload = response.json()
        if not isinstance(payload, dict):
            raise ApiError(f"{method} {path}: ожидался JSON object, получено {type(payload).__name__}")
        return payload

    @staticmethod
    def _assert_ok(response: APIResponse, method: str, path: str) -> None:
        if response.ok:
            return
        body = response.text()
        raise ApiError(f"{method} {path}: HTTP {response.status}; {body[:500]}")


def capture_bearer_token(page: Page) -> str | None:
    """Reload the dashboard and read the bearer token from the UI's own API request."""
    with page.expect_request("**/api/edge*") as request_info:
        page.reload(wait_until="domcontentloaded")
    authorization = request_info.value.headers.get("authorization", "")
    return authorization[7:] if authorization.lower().startswith("bearer ") else None


def create_api_client(playwright: Playwright, api_url: str, token: str | None) -> DrillCloudApi:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = playwright.request.new_context(base_url=f"{api_url.rstrip('/')}/", extra_http_headers=headers)
    return DrillCloudApi(request)
