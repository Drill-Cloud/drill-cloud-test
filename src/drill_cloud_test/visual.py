from __future__ import annotations

from collections.abc import Sequence
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import Locator, Page, ViewportSize

VISUAL_STABILITY_STYLE = """
*, *::before, *::after {
  animation: none !important;
  caret-color: transparent !important;
  font-family: Arial, "Liberation Sans", sans-serif !important;
  transition: none !important;
}
html {
  scrollbar-width: none !important;
}
::-webkit-scrollbar {
  display: none !important;
}
"""
VISUAL_VIEWPORT: ViewportSize = {"width": 1_440, "height": 1_200}


def assert_visual_snapshot(
    page: Page,
    *,
    name: str,
    browser_name: str,
    update: bool,
    mask: Sequence[Locator] = (),
    max_changed_ratio: float = 0.01,
) -> None:
    """Сравнивает страницу с утверждённым PNG и сохраняет понятный diff при ошибке."""
    baseline = Path("tests/visual_baselines") / browser_name / name
    page.set_viewport_size(VISUAL_VIEWPORT)
    page.evaluate("() => document.fonts.ready")
    actual_bytes = page.screenshot(
        full_page=True,
        animations="disabled",
        mask=list(mask),
        style=VISUAL_STABILITY_STYLE,
    )

    if update:
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_bytes(actual_bytes)
        return

    if not baseline.exists():
        raise AssertionError(
            f"Нет visual baseline {baseline}. Проверьте страницу и запустите тест с E2E_UPDATE_SNAPSHOTS=true."
        )

    expected = Image.open(baseline).convert("RGB")
    actual = Image.open(BytesIO(actual_bytes)).convert("RGB")
    artifacts = Path("test-results/visual") / browser_name

    if expected.size != actual.size:
        _save_artifacts(artifacts, name, actual, None)
        raise AssertionError(
            f"Размер страницы изменился: baseline={expected.size}, actual={actual.size}. "
            f"Фактический снимок: {artifacts / name}"
        )

    difference = ImageChops.difference(expected, actual)
    significant = difference.convert("L").point(lambda value: 255 if value > 12 else 0)
    changed_pixels = sum(significant.histogram()[1:])
    changed_ratio = changed_pixels / (actual.width * actual.height)

    if changed_ratio > max_changed_ratio:
        _save_artifacts(artifacts, name, actual, difference)
        raise AssertionError(
            f"Visual diff {changed_ratio:.2%} превышает допуск {max_changed_ratio:.2%}. Снимок и diff: {artifacts}"
        )


def _save_artifacts(
    directory: Path,
    name: str,
    actual: Image.Image,
    difference: Image.Image | None,
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    actual.save(directory / name)
    if difference is not None:
        difference.save(directory / f"{Path(name).stem}-diff.png")
