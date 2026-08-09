from __future__ import annotations

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from drill_cloud_test.config import TestConfig


class LoginPage:
    """Keycloak login form; selectors support standard and localized themes."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username = page.locator("#username, input[name='username']").first
        self.password = page.locator("#password, input[name='password']").first
        self.submit = page.locator("#kc-login, input[type='submit'], button[type='submit']").first

    def is_visible(self, timeout_ms: int = 3_000) -> bool:
        try:
            self.username.wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def sign_in(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()

    def assert_error(self) -> None:
        error = self.page.locator("#input-error, .alert-error, .pf-v5-c-alert, .kc-feedback-text").first
        expect(error).to_be_visible()


def ensure_authenticated(page: Page, config: TestConfig) -> None:
    """Open the dashboard and complete Keycloak login only when it is requested."""
    page.goto("/edges", wait_until="domcontentloaded")
    dashboard_heading = page.get_by_role("heading", name="Буровые установки", exact=True)
    try:
        dashboard_heading.wait_for(state="visible", timeout=5_000)
        return
    except PlaywrightTimeoutError:
        pass

    login = LoginPage(page)
    if config.auth_mode == "disabled":
        raise AssertionError("UI запросил вход, хотя E2E_AUTH_MODE=disabled")
    if not login.is_visible(config.timeout_ms):
        raise AssertionError(f"Не найдены ни dashboard, ни форма Keycloak. Текущий URL: {page.url}")
    if not config.username or not config.password:
        raise AssertionError("Keycloak запросил вход: задайте E2E_USERNAME и E2E_PASSWORD в .env")

    login.sign_in(config.username, config.password)
    expect(dashboard_heading).to_be_visible(timeout=config.timeout_ms)
