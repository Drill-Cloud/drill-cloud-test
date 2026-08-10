from __future__ import annotations

import argparse
import json
import math
import os
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv


def publish(api_url: str, edge_id: str, api_key: str | None, duration_seconds: int, interval_seconds: float) -> None:
    endpoint = f"{api_url.rstrip('/')}/ingest/{quote(edge_id)}"
    deadline = time.monotonic() + duration_seconds
    sequence = 0

    while time.monotonic() < deadline:
        value = round(80 + math.sin(sequence / 2) * 10 + sequence * 0.01, 3)
        body = json.dumps({"values": {"e2e-live": value}}).encode()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key

        request = Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=10) as response:
                if response.status >= 300:
                    raise RuntimeError(f"HTTP {response.status}")
        except HTTPError as error:
            raise SystemExit(f"Ingest failed: HTTP {error.code}; {error.read().decode(errors='replace')}") from error

        print(f"published e2e-live={value}")
        sequence += 1
        time.sleep(interval_seconds)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Publish a changing E2E value through Drill Cloud ingest")
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    api_url = os.getenv("E2E_API_URL", "http://localhost:5173/api")
    edge_id = os.getenv("E2E_EDGE_ID", "e2e-main")
    if not edge_id.startswith("e2e-"):
        raise SystemExit("Live publisher разрешён только для edge ID с префиксом 'e2e-'")
    publish(api_url, edge_id, os.getenv("E2E_INGEST_API_KEY") or None, args.duration, args.interval)


if __name__ == "__main__":
    main()
