from __future__ import annotations

import math
from datetime import datetime
from zoneinfo import ZoneInfo


def _yen(value: float) -> str:
    return f"{value:,.0f}円"


def _signed(value: float, suffix: str = "") -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:,.2f}{suffix}"


def _signed_truncated_yen(value: float) -> str:
    truncated = math.trunc(value)
    sign = "+" if truncated > 0 else ""
    return f"{sign}{truncated:,}円"


def _fund_high_diff(item: dict) -> str:
    diff = float(item["diff_from_high"])
    if diff == 0:
        return "最高値"
    pct = float(item.get("diff_from_high_pct", 0))
    return f"{_signed_truncated_yen(diff)} / {_signed(pct, '%')}"


def format_report(data: dict, timezone: str = "Asia/Tokyo") -> str:
    now = datetime.now(ZoneInfo(timezone))
    lines = [f"**パーソナル朝刊 {now:%Y-%m-%d}**", ""]

    # 天気予報の記事
    weather = data.get("weather", {})
    lines.append("### 天気予報")
    if weather.get("ok"):
        lines.append(
            f'{weather["location"]}: {weather["condition"]} '
            f'{weather["temp_min"]:.0f}-{weather["temp_max"]:.0f}℃ / 降水確率 {weather["precipitation_probability"]}%'
        )
    else:
        lines.append(f'- {weather.get("message", "取得できませんでした。")}')
    lines.append("")

    # BOTヘルスチェック
    health = data.get("healthcheck", {})
    lines.append("### BOTヘルスチェック")
    for item in health.get("items", []):
        if item.get("ok"):
            lines.append(f'- {item["name"]}: OK (HTTP {item["status_code"]})')
        elif "status_code" in item:
            lines.append(
                f'- {item["name"]}: NG (HTTP {item["status_code"]}, expected {item["expected_status"]})'
            )
        else:
            lines.append(f'- {item.get("name", "BOT")}: NG ({item.get("error", "unknown error")})')
    if not health.get("items"):
        lines.append(f'- {health.get("message", "対象なし")}')
    lines.append("")

    # Googleカレンダーの予定
    calendar = data.get("google_calendar", {})
    lines.append("### 今日の予定")
    if calendar.get("items"):
        for item in calendar["items"]:
            start = datetime.fromisoformat(item["start"])
            lines.append(f'- {start:%H:%M} {item["summary"]}')
    else:
        lines.append("- 予定はありません。")
    lines.append("")


    funds = data.get("funds", {})
    lines.append("### 投資信託")
    for item in funds.get("items", []):
        if item.get("ok"):
            lines.append(f'- {item["name"]}: {_yen(item["nav"])} (最高値差 {_fund_high_diff(item)})')
        else:
            lines.append(f'- {item.get("name", item.get("id", "投信"))}: 取得失敗 ({item.get("error")})')
    if not funds.get("items"):
        lines.append(f'- {funds.get("message", "対象なし")}')
    lines.append("")

    for section, title in [("stocks", "株式"), ("indexes", "指数")]:
        block = data.get(section, {})
        lines.append(f"### {title}")
        for item in block.get("items", []):
            if item.get("ok"):
                lines.append(f'- {item["label"]}: {item["close"]:,.2f} ({_signed(item["change"])} / {_signed(item["change_pct"], "%")})')
            else:
                lines.append(f'- {item.get("label", item.get("symbol", title))}: 取得失敗 ({item.get("error")})')
        if not block.get("items"):
            lines.append(f'- {block.get("message", "対象なし")}')
        lines.append("")

    # diary = data.get("audio_diary", {})
    # lines.append("### 昨日の音声日記")
    # lines.append(diary.get("summary") or diary.get("message") or "要約はありません。")
    # lines.append("")

    # rss = data.get("rss", {})
    # lines.append("### ニュース（RSS） 総合要約")
    # lines.append(rss.get("summary") or rss.get("message") or "要約はありません。")
    # if rss.get("items"):
    #     lines.append("")
    #     lines.append("主な記事:")
    #     for item in rss["items"]:
    #         lines.append(f'- [［{item["source"]}］{item["title"]}]({item["link"]})')
    # lines.append("")


    return "\n".join(lines).strip()
