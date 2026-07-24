from __future__ import annotations

from datetime import datetime, timedelta, time
from pathlib import Path
from zoneinfo import ZoneInfo

from src.services import google_drive, openai_client


def collect(config: dict, now: datetime | None = None) -> dict:
    folder_id = config.get("folder_id")
    if not folder_id:
        return {"ok": False, "message": "audio_diary.json に folder_id がありません。", "items": []}

    tz = ZoneInfo(config.get("timezone", "Asia/Tokyo"))
    current = now.astimezone(tz) if now else datetime.now(tz)
    target = current.date() - timedelta(days=1)
    start = datetime.combine(target, time.min, tzinfo=tz)
    end = start + timedelta(days=1)

    files = google_drive.list_files(folder_id, start.isoformat(), end.isoformat())
    if not files:
        return {"ok": True, "date": target.isoformat(), "items": [], "summary": "昨日の音声日記は見つかりませんでした。"}

    cache_dir = Path(config.get("download_dir", "tmp/audio_diary"))
    transcripts = []
    for file in files:
        suffix = Path(file["name"]).suffix or ".audio"
        path = google_drive.download_file(file["id"], cache_dir / f'{file["id"]}{suffix}')
        text = openai_client.transcribe_audio(path)
        transcripts.append({"name": file["name"], "transcript": text})

    joined = "\n\n".join(f'### {item["name"]}\n{item["transcript"]}' for item in transcripts)
    summary = openai_client.summarize_text(
        joined,
        "あなたは日記の振り返りアシスタントです。昨日の出来事、感情、気づき、今日への示唆を日本語で簡潔にまとめてください。",
    )
    return {"ok": True, "date": target.isoformat(), "items": transcripts, "summary": summary}
