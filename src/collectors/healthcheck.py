from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import requests


def collect(config: dict) -> dict:
    bots = config.get("bots", [])
    if not bots:
        return {"ok": False, "message": "healthcheck.json has no bots.", "items": []}

    items = []
    for bot in bots:
        name = bot["name"]
        url = bot["url"]
        expected_status = int(bot.get("expected_status", 200))
        try:
            resp = requests.get(url, timeout=int(bot.get("timeout_seconds", 30)))
            status_code = resp.status_code
            items.append(
                {
                    "ok": status_code == expected_status,
                    "name": name,
                    "url": url,
                    "status_code": status_code,
                    "expected_status": expected_status,
                }
            )
        except Exception as exc:
            items.append(
                {
                    "ok": False,
                    "name": name,
                    "url": url,
                    "expected_status": expected_status,
                    "error": str(exc),
                }
            )

    return {
        "ok": all(item["ok"] for item in items),
        "checked_at": datetime.now(ZoneInfo(config.get("timezone", "Asia/Tokyo"))).isoformat(),
        "items": items,
    }
