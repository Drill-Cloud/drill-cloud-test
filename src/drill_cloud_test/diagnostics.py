from __future__ import annotations

from dataclasses import dataclass, field

from playwright.sync_api import ConsoleMessage, Error, Request


@dataclass
class BrowserDiagnostics:
    """Collect browser-side failures without mixing them with test actions."""

    # Playwright stores wrapped bound-method handlers on their owner instance.
    # Therefore this class intentionally keeps __dict__ and must not use slots.

    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    failed_requests: list[str] = field(default_factory=list)

    def on_console(self, message: ConsoleMessage) -> None:
        if message.type == "error":
            self.console_errors.append(f"console: {message.text}")

    def on_page_error(self, error: Error) -> None:
        self.page_errors.append(f"pageerror: {error}")

    def on_request_failed(self, request: Request) -> None:
        failure = request.failure or "unknown error"
        self.failed_requests.append(f"{request.method} {request.url}: {failure}")

    def assert_no_runtime_errors(self) -> None:
        errors = [*self.page_errors, *self.console_errors]
        assert not errors, "Ошибки браузера:\n" + "\n".join(errors)

    def as_text(self) -> str:
        groups = (
            ("Console errors", self.console_errors),
            ("Page errors", self.page_errors),
            ("Failed requests", self.failed_requests),
        )
        sections = [f"{title}:\n" + ("\n".join(values) if values else "—") for title, values in groups]
        return "\n\n".join(sections)
