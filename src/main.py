from __future__ import annotations

import argparse
import traceback
from typing import Callable

from src import config
from src.collectors import audio_diary, funds, google_calendar, healthcheck, indexes, rss, stocks, weather
from src.formatters.morning_report import format_report
from src.formatters.public_page import write_public_pages
from src.services.discord import post_to_discord


Collector = Callable[[dict], dict]


def _safe_collect(name: str, fn: Collector, cfg: dict) -> dict:
    try:
        return fn(cfg)
    except Exception as exc:
        print(str(exc))
        return {"ok": False, "message": f"{name} の取得に失敗しました。", "error": str(exc), "traceback": traceback.format_exc()}


def collect_all(is_dry_run: bool) -> dict:
    return {
        "weather": _safe_collect("weather", weather.collect, config.config("weather", {})),                     # 天気予報
        "funds": _safe_collect("funds", funds.collect, config.config("funds", {})),                             # 投資信託
        "stocks": _safe_collect("stocks", stocks.collect, config.config("stocks", {})),                         # 株価
        "indexes": _safe_collect("indexes", indexes.collect, config.config("indexes", {})),                     # 指数
        "google_calendar": _safe_collect("google_calendar", google_calendar.collect, config.config("google_calendar", {})), # 公開Googleカレンダー
        "healthcheck": _safe_collect("healthcheck", healthcheck.collect, config.config("healthcheck", {})),     # Botヘルスチェック
        # "audio_diary": _safe_collect("audio_diary", audio_diary.collect, config.config("audio_diary", {})),     # 音声日記の解析
        # "rss": _safe_collect("rss", rss.collect, config.config("rss", {})),                                     # RSS
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Discord に投稿せず標準出力へ表示します")
    args = parser.parse_args()

    app_cfg = config.config("app", {"timezone": "Asia/Tokyo"})
    timezone = app_cfg.get("timezone", "Asia/Tokyo")
    data = collect_all(args.dry_run)
    report = format_report(data, timezone=timezone)

    if args.dry_run:
        print(report)
    else:
        write_public_pages(data, timezone=timezone)
        post_to_discord(report)


if __name__ == "__main__":
    main()
