from __future__ import annotations

from datetime import datetime
from email.utils import format_datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo


def _yen(value: float) -> str:
    return f"{value:,.0f}円"


def _signed(value: float, suffix: str = "") -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:,.2f}{suffix}"


def _date_label(now: datetime) -> str:
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    return f"{now.year}年{now.month}月{now.day}日（{weekdays[now.weekday()]}）"


def _format_weather(weather: dict) -> str:
    if weather.get("ok"):
        return (
            f'{weather["condition"]}、'
            f'最低気温{weather["temp_min"]:.0f}度、最高気温{weather["temp_max"]:.0f}度、'
            f'降水確率{weather["precipitation_probability"]}パーセントです。'
        )
    return weather.get("message", "天気は取得できませんでした。")


def _format_funds(funds: dict) -> list[str]:
    lines = []
    for item in funds.get("items", []):
        if item.get("ok"):
            lines.append(
                f'{item["name"]}は現在{_yen(item["nav"])}、'
                f'最高値との差は{_signed(item.get("diff_from_high_pct", 0), "パーセント")}です。'
            )
        else:
            lines.append(f'{item.get("name", item.get("id", "投資信託"))}は取得に失敗しました。')
    return lines or [funds.get("message", "投資信託の対象はありません。")]


def _format_quotes(block: dict, empty_message: str) -> list[str]:
    lines = []
    for item in block.get("items", []):
        if item.get("ok"):
            lines.append(
                f'{item["label"]}は{item["close"]:,.2f}、'
                f'前日比{_signed(item["change"])}、{_signed(item["change_pct"], "パーセント")}です。'
            )
        else:
            lines.append(f'{item.get("label", item.get("symbol", "銘柄"))}は取得に失敗しました。')
    return lines or [block.get("message", empty_message)]


def format_public_text(data: dict, timezone: str = "Asia/Tokyo") -> str:
    now = datetime.now(ZoneInfo(timezone))
    lines = [
        f"パーソナル朝刊、{_date_label(now)}です。",
        "",
        "天気です。",
        _format_weather(data.get("weather", {})),
        "",
        "投資信託です。",
        *[f"- {line}" for line in _format_funds(data.get("funds", {}))],
        "",
        "株価です。",
        *[f"- {line}" for line in _format_quotes(data.get("stocks", {}), "株価の対象はありません。")],
        "",
        "指数です。",
        *[f"- {line}" for line in _format_quotes(data.get("indexes", {}), "指数の対象はありません。")],
    ]
    return "\n".join(lines).strip()


def format_public_html(data: dict, timezone: str = "Asia/Tokyo") -> str:
    now = datetime.now(ZoneInfo(timezone))
    text = format_public_text(data, timezone)
    body = escape(text).replace("\n", "<br>\n")
    generated = escape(now.isoformat(timespec="seconds"))
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>パーソナル朝刊</title>
</head>
<body>
  <main>
    <h1>パーソナル朝刊</h1>
    <p>更新日時: <time datetime="{generated}">{escape(_date_label(now))}</time></p>
    <article>
      <p>{body}</p>
    </article>
  </main>
</body>
</html>
"""


def format_rss(data: dict, timezone: str = "Asia/Tokyo") -> str:
    now = datetime.now(ZoneInfo(timezone))
    text = format_public_text(data, timezone)
    pub_date = format_datetime(now)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>パーソナル朝刊</title>
    <description>Amazon Echo読み上げ用のパーソナル朝刊です。</description>
    <language>ja-jp</language>
    <lastBuildDate>{escape(pub_date)}</lastBuildDate>
    <item>
      <title>パーソナル朝刊 {escape(now.strftime("%Y-%m-%d"))}</title>
      <description>{escape(text)}</description>
      <pubDate>{escape(pub_date)}</pubDate>
      <guid isPermaLink="false">morning-report-{escape(now.strftime("%Y-%m-%d"))}</guid>
    </item>
  </channel>
</rss>
"""


def write_public_pages(data: dict, output_dir: str | Path = "doc", timezone: str = "Asia/Tokyo") -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "index.html").write_text(format_public_html(data, timezone), encoding="utf-8")
    (path / "feed.xml").write_text(format_rss(data, timezone), encoding="utf-8")
    (path / "alexa.txt").write_text(format_public_text(data, timezone) + "\n", encoding="utf-8")
