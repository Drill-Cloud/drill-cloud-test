import pytest

from scripts.seed_test_data import _edge_ids, _require_safe_ids


@pytest.mark.unit
def test_seed_uses_safe_defaults_for_blank_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("E2E_EDGE_ID", "E2E_NO_VIDEO_EDGE_ID", "E2E_VIDEO_EDGE_ID"):
        monkeypatch.setenv(name, "")

    assert _edge_ids() == ("e2e-main", "e2e-no-video", "e2e-video")


@pytest.mark.unit
def test_seed_rejects_non_e2e_edge() -> None:
    with pytest.raises(SystemExit, match="префиксом 'e2e-'"):
        _require_safe_ids(("e2e-main", "production-edge", "e2e-video"))
