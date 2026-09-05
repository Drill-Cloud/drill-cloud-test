from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal
from urllib.parse import urljoin

from dotenv import load_dotenv

AuthMode = Literal["auto", "required", "disabled"]
BrowserName = Literal["chromium", "firefox", "webkit"]


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} должен быть true или false, получено: {value!r}")


def _read_int(name: str, default: int, *, minimum: int = 0) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} должен быть целым числом, получено: {raw!r}") from error
    if value < minimum:
        raise ValueError(f"{name} должен быть не меньше {minimum}, получено: {value}")
    return value


def _optional(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _normalize_url(value: str) -> str:
    return value.strip().rstrip("/")


@dataclass(frozen=True, slots=True)
class TestConfig:
    __test__: ClassVar[bool] = False

    base_url: str
    api_url: str
    auth_mode: AuthMode
    username: str | None
    password: str | None
    api_token: str | None
    admin_username: str | None
    admin_password: str | None
    edge_username: str | None
    edge_password: str | None
    no_role_username: str | None
    no_role_password: str | None
    edge_id: str | None
    forbidden_edge_id: str | None
    video_edge_id: str | None
    no_video_edge_id: str | None
    indicator_query: str | None
    history_tag_query: str | None
    live_tag: str | None
    require_history_data: bool
    require_video_playback: bool
    live_wait_seconds: int
    sse_observe_seconds: int
    max_current_requests: int
    visual_enabled: bool
    update_snapshots: bool
    database_url: str | None
    ingest_api_key: str | None
    ui_commit: str | None
    cloud_commit: str | None
    browser: BrowserName
    headless: bool
    slow_mo_ms: int
    timeout_ms: int
    viewport_width: int
    viewport_height: int

    @property
    def health_url(self) -> str:
        return urljoin(f"{self.api_url}/", "health")

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> TestConfig:
        load_dotenv(env_file or Path.cwd() / ".env", override=False)

        auth_mode = os.getenv("E2E_AUTH_MODE", "auto").strip().lower()
        if auth_mode not in {"auto", "required", "disabled"}:
            raise ValueError("E2E_AUTH_MODE должен быть auto, required или disabled")

        browser = os.getenv("E2E_BROWSER", "chromium").strip().lower()
        if browser not in {"chromium", "firefox", "webkit"}:
            raise ValueError("E2E_BROWSER должен быть chromium, firefox или webkit")

        base_url = _normalize_url(os.getenv("E2E_BASE_URL", "http://localhost:5173"))
        api_url = _normalize_url(os.getenv("E2E_API_URL", f"{base_url}/api"))

        return cls(
            base_url=base_url,
            api_url=api_url,
            auth_mode=auth_mode,  # type: ignore[arg-type]
            username=_optional("E2E_USERNAME"),
            password=_optional("E2E_PASSWORD"),
            api_token=_optional("E2E_API_TOKEN"),
            admin_username=_optional("E2E_ADMIN_USERNAME"),
            admin_password=_optional("E2E_ADMIN_PASSWORD"),
            edge_username=_optional("E2E_EDGE_USERNAME"),
            edge_password=_optional("E2E_EDGE_PASSWORD"),
            no_role_username=_optional("E2E_NO_ROLE_USERNAME"),
            no_role_password=_optional("E2E_NO_ROLE_PASSWORD"),
            edge_id=_optional("E2E_EDGE_ID"),
            forbidden_edge_id=_optional("E2E_FORBIDDEN_EDGE_ID"),
            video_edge_id=_optional("E2E_VIDEO_EDGE_ID"),
            no_video_edge_id=_optional("E2E_NO_VIDEO_EDGE_ID"),
            indicator_query=_optional("E2E_INDICATOR_QUERY"),
            history_tag_query=_optional("E2E_HISTORY_TAG_QUERY"),
            live_tag=_optional("E2E_LIVE_TAG"),
            require_history_data=_read_bool("E2E_REQUIRE_HISTORY_DATA", False),
            require_video_playback=_read_bool("E2E_REQUIRE_VIDEO_PLAYBACK", False),
            live_wait_seconds=_read_int("E2E_LIVE_WAIT_SECONDS", 30, minimum=1),
            sse_observe_seconds=_read_int("E2E_SSE_OBSERVE_SECONDS", 8, minimum=2),
            max_current_requests=_read_int("E2E_MAX_CURRENT_REQUESTS", 12, minimum=2),
            visual_enabled=_read_bool("E2E_VISUAL_ENABLED", True),
            update_snapshots=_read_bool("E2E_UPDATE_SNAPSHOTS", False),
            database_url=_optional("E2E_DATABASE_URL"),
            ingest_api_key=_optional("E2E_INGEST_API_KEY"),
            ui_commit=_optional("E2E_UI_COMMIT"),
            cloud_commit=_optional("E2E_CLOUD_COMMIT"),
            browser=browser,  # type: ignore[arg-type]
            headless=_read_bool("E2E_HEADLESS", True),
            slow_mo_ms=_read_int("E2E_SLOW_MO_MS", 0),
            timeout_ms=_read_int("E2E_TIMEOUT_MS", 20_000, minimum=1_000),
            viewport_width=_read_int("E2E_VIEWPORT_WIDTH", 1_440, minimum=320),
            viewport_height=_read_int("E2E_VIEWPORT_HEIGHT", 1_000, minimum=320),
        )
