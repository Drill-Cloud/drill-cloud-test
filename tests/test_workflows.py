from pathlib import Path

import pytest
import yaml


@pytest.mark.unit
def test_github_workflows_are_valid_yaml() -> None:
    """Ловит синтаксические ошибки CI до отправки ветки в GitHub."""
    workflow_files = sorted(Path(".github/workflows").glob("*.yml"))
    assert workflow_files, "В проекте не найдены GitHub Actions workflows"

    for workflow_file in workflow_files:
        document = yaml.load(workflow_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        assert isinstance(document, dict), f"{workflow_file} должен содержать YAML-объект"
        assert "name" in document, f"В {workflow_file} отсутствует name"
        assert "on" in document, f"В {workflow_file} отсутствует on"
        assert "jobs" in document, f"В {workflow_file} отсутствует jobs"
