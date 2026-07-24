from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import requests

from src.storage.json_store import JsonStore


class _NavSpanParser(HTMLParser):
    def __init__(self, class_names: set[str]):
        super().__init__()
        self.class_names = class_names
        self._capturing = False
        self._depth = 0
        self.value = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._capturing:
            self._depth += 1
            return

        if tag != "span":
            return

        attr = dict(attrs)
        classes = set((attr.get("class") or "").split())
        if self.class_names.issubset(classes):
            self._capturing = True
            self._depth = 1

    def handle_data(self, data: str) -> None:
        if self._capturing:
            self.value += data

    def handle_endtag(self, tag: str) -> None:
        if self._capturing:
            self._depth -= 1
            if self._depth <= 0:
                self._capturing = False


def _parse_nav_from_html(html: str, class_names: set[str]) -> float:
    parser = _NavSpanParser(class_names)
    parser.feed(html)
    if not parser.value.strip():
        raise ValueError("NAV span was not found.")

    normalized = parser.value.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", normalized)
    if not match:
        raise ValueError(f"NAV value could not be parsed: {parser.value!r}")
    return float(match.group(0))


def _fetch_nav(item: dict) -> float:
    headers = {
        "User-Agent": "MyNewsPaper/1.0 (+https://github.com/actions)",
    }
    resp = requests.get(item["url"], headers=headers, timeout=30)
    resp.raise_for_status()
    classes = set(item.get("nav_classes", ["h3", "font-weight-bold"]))
    return _parse_nav_from_html(resp.text, classes)


def collect(config: dict, watermark_path: str | Path = "data/funds_high_watermark.json") -> dict:
    funds = config.get("funds", [])
    if not funds:
        return {"ok": False, "message": "funds.json has no funds.", "items": []}

    store = JsonStore(watermark_path)
    high = store.load({})
    items = []
    changed = False

    for fund in funds:
        key = fund.get("id") or fund["name"]
        try:
            nav = _fetch_nav(fund)
            if key not in high:
                high[key] = nav
                changed = True
            prev_high = float(high[key])
            if nav > prev_high:
                high[key] = nav
                prev_high = nav
                changed = True
            items.append(
                {
                    "ok": True,
                    "id": key,
                    "name": fund["name"],
                    "nav": nav,
                    "high_watermark": prev_high,
                    "diff_from_high": nav - prev_high,
                    "diff_from_high_pct": ((nav - prev_high) / prev_high * 100) if prev_high else 0,
                }
            )
        except Exception as exc:
            items.append({"ok": False, "id": key, "name": fund.get("name", key), "error": str(exc)})

    if changed:
        store.save(high)
    return {"ok": True, "items": items}
