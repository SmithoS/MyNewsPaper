from __future__ import annotations

from src.collectors.stocks import collect as collect_quotes


def collect(config: dict) -> dict:
    return collect_quotes({"symbols": config.get("indexes", [])})
