from __future__ import annotations

from drill_cloud_test.api import JsonObject


def default_ui_settings() -> JsonObject:
    """Mirror frontend defaults for isolated API fixtures and cleanup only."""
    return {
        "player": {
            "liveBufferLatencyMaxLatency": 24,
            "liveBufferLatencyMinRemain": 8,
            "stashInitialSize": 256 * 1024,
            "autoCleanupMaxBackwardDuration": 20,
            "autoCleanupMinBackwardDuration": 8,
        },
        "liveChart": {
            "windowMinutes": 25,
            "shiftIntervalMs": 5_000,
            "fallbackPollingMs": 1_000,
            "granulate": "5 seconds",
            "maxPointsPerTag": 300,
        },
        "archiveChart": {"defaultPeriodHours": 24},
        "interface": {"sidebarCollapsed": False},
    }
