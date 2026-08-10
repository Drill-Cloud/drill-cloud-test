from __future__ import annotations

from copy import deepcopy

import pytest
from playwright.sync_api import Playwright, expect

from drill_cloud_test.api import JsonObject, capture_bearer_token, create_api_client
from drill_cloud_test.config import TestConfig
from drill_cloud_test.pages import DashboardPage, EdgePage
from drill_cloud_test.sessions import AuthenticatedSessionFactory
from drill_cloud_test.ui_settings import default_ui_settings


def _require_credentials(username: str | None, password: str | None, variables: str) -> tuple[str, str]:
    if not username or not password:
        pytest.skip(f"Для role-теста задайте {variables}")
    return username, password


@pytest.mark.case("AUTH-03-admin")
@pytest.mark.p1
@pytest.mark.auth
def test_admin_user_can_see_edges(role_session_factory: AuthenticatedSessionFactory, test_config: TestConfig) -> None:
    """Администратор получает непустой список доступных буровых."""
    credentials = _require_credentials(
        test_config.admin_username,
        test_config.admin_password,
        "E2E_ADMIN_USERNAME и E2E_ADMIN_PASSWORD",
    )
    with role_session_factory.open("admin", *credentials) as session:
        dashboard = DashboardPage(session.page)
        dashboard.assert_loaded()
        expect(dashboard.cards.first).to_be_visible()


@pytest.mark.case("AUTH-03-edge-user")
@pytest.mark.p1
@pytest.mark.auth
def test_edge_user_cannot_open_forbidden_edge(
    role_session_factory: AuthenticatedSessionFactory, test_config: TestConfig
) -> None:
    """Пользователь ограниченной буровой не получает current-данные чужой буровой."""
    credentials = _require_credentials(
        test_config.edge_username,
        test_config.edge_password,
        "E2E_EDGE_USERNAME и E2E_EDGE_PASSWORD",
    )
    if not test_config.forbidden_edge_id:
        pytest.skip("Для проверки 403 задайте E2E_FORBIDDEN_EDGE_ID")

    with role_session_factory.open("edge-user", *credentials) as session:
        edge = EdgePage(session.page)
        with session.page.expect_response(
            lambda response: "/api/current?" in response.url and "/events" not in response.url
        ) as response_info:
            edge.open_edge(test_config.forbidden_edge_id)
        assert response_info.value.status == 403


@pytest.mark.case("AUTH-03-no-role")
@pytest.mark.p1
@pytest.mark.auth
def test_user_without_edge_roles_sees_empty_list(
    role_session_factory: AuthenticatedSessionFactory, test_config: TestConfig
) -> None:
    """Пользователь без edge-ролей видит безопасный пустой dashboard."""
    credentials = _require_credentials(
        test_config.no_role_username,
        test_config.no_role_password,
        "E2E_NO_ROLE_USERNAME и E2E_NO_ROLE_PASSWORD",
    )
    with role_session_factory.open("no-role", *credentials) as session:
        dashboard = DashboardPage(session.page)
        dashboard.assert_loaded()
        expect(dashboard.cards).to_have_count(0)
        expect(session.page.get_by_text("В cloud-v3 пока нет буровых", exact=True)).to_be_visible()


@pytest.mark.case("SETTINGS-03-user-isolation")
@pytest.mark.p1
@pytest.mark.auth
@pytest.mark.settings
@pytest.mark.serial
def test_ui_settings_are_isolated_between_users(
    role_session_factory: AuthenticatedSessionFactory,
    test_config: TestConfig,
    playwright: Playwright,
) -> None:
    """Изменение admin-настроек не подменяет настройки edge-пользователя."""
    admin_credentials = _require_credentials(
        test_config.admin_username,
        test_config.admin_password,
        "E2E_ADMIN_USERNAME и E2E_ADMIN_PASSWORD",
    )
    edge_credentials = _require_credentials(
        test_config.edge_username,
        test_config.edge_password,
        "E2E_EDGE_USERNAME и E2E_EDGE_PASSWORD",
    )

    with (
        role_session_factory.open("settings-admin", *admin_credentials) as admin_session,
        role_session_factory.open("settings-edge", *edge_credentials) as edge_session,
    ):
        admin_api = create_api_client(playwright, test_config.api_url, capture_bearer_token(admin_session.page))
        edge_api = create_api_client(playwright, test_config.api_url, capture_bearer_token(edge_session.page))
        original_admin: JsonObject | None = None
        original_admin_loaded = False
        try:
            original_admin = admin_api.get_ui_settings().get("settings")
            original_admin_loaded = True
            original_edge = deepcopy(edge_api.get_ui_settings().get("settings"))
            changed_admin = deepcopy(original_admin or default_ui_settings())
            changed_admin["liveChart"]["windowMinutes"] = 37

            admin_api.save_ui_settings(changed_admin)
            assert edge_api.get_ui_settings().get("settings") == original_edge
        finally:
            if original_admin_loaded:
                if original_admin is None:
                    admin_api.delete_ui_settings()
                else:
                    admin_api.save_ui_settings(original_admin)
            admin_api.close()
            edge_api.close()
