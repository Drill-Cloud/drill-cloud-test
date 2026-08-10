from __future__ import annotations

import inspect
import re
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, Page, Playwright

from drill_cloud_test.api import DrillCloudApi, capture_bearer_token, create_api_client
from drill_cloud_test.config import TestConfig
from drill_cloud_test.diagnostics import BrowserDiagnostics
from drill_cloud_test.pages import DashboardPage
from drill_cloud_test.pages.login import ensure_authenticated
from drill_cloud_test.sessions import AuthenticatedSessionFactory


def _safe_artifact_name(node_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", node_id).strip("_")


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    try:
        return TestConfig.from_env()
    except ValueError as error:
        raise pytest.UsageError(str(error)) from error


@pytest.fixture(scope="session")
def browser_name(test_config: TestConfig) -> str:
    return test_config.browser


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict[str, Any], test_config: TestConfig) -> dict[str, Any]:
    return {
        **browser_type_launch_args,
        "headless": test_config.headless,
        "slow_mo": test_config.slow_mo_ms,
    }


@pytest.fixture(scope="session")
def auth_storage_state(browser: Browser, test_config: TestConfig, tmp_path_factory: pytest.TempPathFactory) -> Path:
    state_path = tmp_path_factory.mktemp("auth") / "storage-state.json"
    context = browser.new_context(
        base_url=test_config.base_url,
        locale="ru-RU",
        viewport={"width": test_config.viewport_width, "height": test_config.viewport_height},
    )
    try:
        page = context.new_page()
        page.set_default_timeout(test_config.timeout_ms)
        ensure_authenticated(page, test_config)
        context.storage_state(path=state_path)
    finally:
        context.close()
    return state_path


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], test_config: TestConfig, auth_storage_state: Path
) -> dict[str, Any]:
    return {
        **browser_context_args,
        "base_url": test_config.base_url,
        "locale": "ru-RU",
        "storage_state": auth_storage_state,
        "viewport": {
            "width": test_config.viewport_width,
            "height": test_config.viewport_height,
        },
    }


@pytest.fixture(scope="session")
def role_session_factory(
    browser: Browser, test_config: TestConfig, tmp_path_factory: pytest.TempPathFactory
) -> AuthenticatedSessionFactory:
    state_directory = tmp_path_factory.mktemp("role-auth")
    return AuthenticatedSessionFactory(browser, test_config, state_directory)


@pytest.fixture
def diagnostics(page: Page, request: pytest.FixtureRequest) -> Generator[BrowserDiagnostics, None, None]:
    result = BrowserDiagnostics()
    page.on("console", result.on_console)
    page.on("pageerror", result.on_page_error)
    page.on("requestfailed", result.on_request_failed)
    yield result

    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        artifact_dir = Path("test-results") / _safe_artifact_name(request.node.nodeid)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "browser-diagnostics.txt").write_text(result.as_text(), encoding="utf-8")


@pytest.fixture
def app_page(page: Page, test_config: TestConfig, diagnostics: BrowserDiagnostics) -> Page:
    del diagnostics  # dependency starts collection before navigation
    page.set_default_timeout(test_config.timeout_ms)
    ensure_authenticated(page, test_config)
    return page


@pytest.fixture
def edge_id(app_page: Page, test_config: TestConfig) -> str:
    if test_config.edge_id:
        return test_config.edge_id
    return DashboardPage(app_page).discover_edge_id()


@pytest.fixture
def api_token(app_page: Page, test_config: TestConfig) -> str | None:
    """Capture the same bearer token that the UI sends to Drill Cloud API."""
    if test_config.api_token:
        return test_config.api_token
    if test_config.auth_mode == "disabled":
        return None

    token = capture_bearer_token(app_page)
    if token:
        return token
    if test_config.auth_mode == "required":
        raise AssertionError("UI не отправил bearer token в запросе /api/edge")
    return None


@pytest.fixture
def api_client(
    playwright: Playwright, test_config: TestConfig, api_token: str | None
) -> Generator[DrillCloudApi, None, None]:
    client = create_api_client(playwright, test_config.api_url, api_token)
    try:
        yield client
    finally:
        client.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()
    case_marker = item.get_closest_marker("case")
    report.case_id = case_marker.args[0] if case_marker and case_marker.args else "—"
    report.scenario = inspect.getdoc(getattr(item, "function", None)) or "—"
    setattr(item, f"rep_{report.when}", report)


def pytest_report_header(config: pytest.Config) -> list[str]:
    del config
    test_config = TestConfig.from_env()
    return [
        f"Drill Cloud UI: {test_config.base_url}",
        f"Drill Cloud API: {test_config.api_url}",
        f"UI commit: {test_config.ui_commit or 'not specified'}",
        f"Cloud commit: {test_config.cloud_commit or 'not specified'}",
        f"Browser: {test_config.browser}; headless={test_config.headless}",
    ]


def pytest_html_report_title(report: Any) -> None:
    report.title = "Drill Cloud — smoke test report"


def pytest_html_results_table_header(cells: list[str]) -> None:
    cells.insert(1, "<th>Case</th>")
    cells.insert(2, "<th>Scenario</th>")


def pytest_html_results_table_row(report: Any, cells: list[str]) -> None:
    cells.insert(1, f"<td>{report.case_id}</td>")
    cells.insert(2, f"<td>{report.scenario}</td>")
