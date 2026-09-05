from __future__ import annotations

import pytest
from PIL import Image, ImageDraw

from drill_cloud_test.visual import _changed_pixel_ratio


@pytest.mark.unit
def test_visual_diff_ignores_small_antialiasing_noise() -> None:
    expected = Image.new("RGB", (100, 100), "#101010")
    actual = expected.copy()
    ImageDraw.Draw(expected).line((20, 10, 20, 90), fill="#8a8a8a", width=1)
    ImageDraw.Draw(actual).line((20, 10, 20, 90), fill="#9a9a9a", width=1)

    assert _changed_pixel_ratio(expected, actual) == 0


@pytest.mark.unit
def test_visual_diff_detects_structural_change() -> None:
    expected = Image.new("RGB", (100, 100), "#101010")
    actual = expected.copy()
    ImageDraw.Draw(actual).rectangle((20, 20, 79, 79), fill="#f0f0f0")

    assert _changed_pixel_ratio(expected, actual) > 0.25
