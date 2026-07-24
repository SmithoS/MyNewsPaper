from __future__ import annotations

import os
from typing import Iterable

import requests


DISCORD_LIMIT = 1900


def _chunks(text: str, limit: int = DISCORD_LIMIT) -> Iterable[str]:
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < 1:
            cut = limit
        yield text[:cut]
        text = text[cut:].lstrip()
    if text:
        yield text


def post_to_discord(content: str, webhook_url: str | None = None) -> None:
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

    for chunk in _chunks(content):
        resp = requests.post(url, json={"content": chunk}, timeout=30)
        resp.raise_for_status()
