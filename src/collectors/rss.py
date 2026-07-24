from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.services.openai_client import summarize_text


def collect(config: dict) -> dict:
    import feedparser

    feeds = config.get("feeds", [])
    if not feeds:
        return {"ok": False, "message": "rss.json に feeds がありません。", "items": [], "summary": ""}

    limit = int(config.get("max_items", 30))
    tz = ZoneInfo(config.get("timezone", "Asia/Tokyo"))
    since = datetime.now(tz) - timedelta(hours=int(config.get("lookback_hours", 24)))
    items = []

    for feed in feeds:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries[:limit]:
            published = None
            if getattr(entry, "published_parsed", None):
                published = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(tz)
            if published and published < since:
                continue

            items.append(
                {
                    "source": feed.get("label", ""),
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published": published.isoformat() if published else "",
                }
            )

    digest = "\n".join(f'- [{i["source"]}] {i["title"]}\n{i["summary"]}\n{i["link"]}' for i in items)
    summary = summarize_text(
        digest,
        "あなたは朝刊編集者です。RSS記事群から重要トピック、影響、読むべき記事を日本語で総合要約してください。",
    )
    return {"ok": True, "items": items, "summary": summary}
