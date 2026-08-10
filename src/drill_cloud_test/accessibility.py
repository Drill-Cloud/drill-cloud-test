from __future__ import annotations

from playwright.sync_api import Page


def assert_basic_accessibility(page: Page) -> None:
    """Catch inexpensive accessibility regressions without pretending to be a full WCAG audit."""
    duplicate_ids = page.locator("[id]").evaluate_all(
        """
        elements => {
          const counts = new Map();
          for (const element of elements) counts.set(element.id, (counts.get(element.id) || 0) + 1);
          return [...counts.entries()].filter(([, count]) => count > 1).map(([id]) => id);
        }
        """
    )
    assert not duplicate_ids, f"На странице есть повторяющиеся id: {duplicate_ids}"

    unnamed_buttons = page.locator("button").evaluate_all(
        """
        buttons => buttons
          .filter(button => {
            const name = button.getAttribute('aria-label')
              || button.getAttribute('title')
              || button.innerText;
            return !name || !name.trim();
          })
          .map(button => button.outerHTML.slice(0, 200))
        """
    )
    assert not unnamed_buttons, "Кнопки без доступного имени:\n" + "\n".join(unnamed_buttons)

    images_without_alt = page.locator("img:not([alt])").count()
    assert images_without_alt == 0, f"Изображений без alt: {images_without_alt}"


def assert_no_horizontal_overflow(page: Page) -> None:
    dimensions = page.evaluate(
        """
        () => ({
          viewport: window.innerWidth,
          document: document.documentElement.scrollWidth,
        })
        """
    )
    assert dimensions["document"] <= dimensions["viewport"] + 1, (
        f"Горизонтальный overflow: document={dimensions['document']}px, viewport={dimensions['viewport']}px"
    )
