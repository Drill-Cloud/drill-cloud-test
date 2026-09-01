from __future__ import annotations

from types import SimpleNamespace

import pytest
from conftest import pytest_html_results_table_row


@pytest.mark.unit
def test_html_results_table_row_handles_report_without_case_metadata() -> None:
    """Collection reports without runtest metadata remain renderable."""
    cells = ["<td>result</td>"]

    pytest_html_results_table_row(SimpleNamespace(), cells)

    assert cells == ["<td>result</td>", "<td>—</td>", "<td>—</td>"]


@pytest.mark.unit
def test_html_results_table_row_renders_case_metadata() -> None:
    """Regular test reports keep the case identifier and scenario columns."""
    cells = ["<td>result</td>"]
    report = SimpleNamespace(case_id="EDGE-01", scenario="Dashboard loads")

    pytest_html_results_table_row(report, cells)

    assert cells == ["<td>result</td>", "<td>EDGE-01</td>", "<td>Dashboard loads</td>"]
