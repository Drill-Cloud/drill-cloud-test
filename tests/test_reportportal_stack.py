from pathlib import Path
from typing import Any, cast

import pytest
import yaml

COMPOSE_PATH = Path("deploy/reportportal/docker-compose.yml")


def _load_compose() -> dict[str, Any]:
    document = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return cast(dict[str, Any], document)


@pytest.mark.unit
def test_reportportal_stack_is_ready_for_portainer_and_npm() -> None:
    compose_text = COMPOSE_PATH.read_text(encoding="utf-8")
    compose = _load_compose()
    services = compose["services"]
    gateway = services["gateway"]

    assert len(services) == 12
    assert all("build" not in service for service in services.values())
    assert "ports" not in gateway
    assert gateway["expose"] == ["8080"]
    assert gateway["container_name"] == "container-reportportal-gateway"
    assert set(gateway["networks"]) == {"reportportal", "proxy"}
    assert compose["networks"]["proxy"] == {"external": True}
    assert "websecure" not in compose_text


@pytest.mark.unit
def test_reportportal_data_uses_stable_named_volumes() -> None:
    compose = _load_compose()

    assert compose["volumes"] == {
        "opensearch": {"name": "reportportal_opensearch"},
        "storage": {"name": "reportportal_storage"},
        "analyzer-storage": {"name": "reportportal_analyzer_storage"},
        "postgres": {"name": "reportportal_postgres"},
    }
