from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path
from types import TracebackType

from playwright.sync_api import Browser, BrowserContext, Page

from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages.login import ensure_authenticated


@dataclass
class AuthenticatedSession:
    """A browser context isolated from the main smoke-test user."""

    context: BrowserContext
    page: Page

    def close(self) -> None:
        self.context.close()

    def __enter__(self) -> AuthenticatedSession:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exception_type, exception, traceback
        self.close()


class AuthenticatedSessionFactory:
    """Creates cached Keycloak storage states for role-specific users."""

    def __init__(self, browser: Browser, config: TestConfig, state_directory: Path) -> None:
        self._browser = browser
        self._config = config
        self._state_directory = state_directory

    def open(self, label: str, username: str, password: str) -> AuthenticatedSession:
        state_path = self._state_path(label)
        role_config = replace(
            self._config,
            auth_mode="required",
            username=username,
            password=password,
        )

        if not state_path.exists():
            self._create_storage_state(state_path, role_config)

        context = self._new_context(storage_state=state_path)
        page = context.new_page()
        page.set_default_timeout(self._config.timeout_ms)
        ensure_authenticated(page, role_config)
        return AuthenticatedSession(context=context, page=page)

    def _create_storage_state(self, state_path: Path, config: TestConfig) -> None:
        context = self._new_context()
        try:
            page = context.new_page()
            page.set_default_timeout(config.timeout_ms)
            ensure_authenticated(page, config)
            context.storage_state(path=state_path)
        finally:
            context.close()

    def _new_context(self, *, storage_state: Path | None = None) -> BrowserContext:
        return self._browser.new_context(
            base_url=self._config.base_url,
            locale="ru-RU",
            storage_state=storage_state,
            viewport={"width": self._config.viewport_width, "height": self._config.viewport_height},
        )

    def _state_path(self, label: str) -> Path:
        safe_label = re.sub(r"[^a-zA-Z0-9_.-]+", "-", label).strip("-")
        return self._state_directory / f"{safe_label}.json"
