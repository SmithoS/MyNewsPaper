from __future__ import annotations

import re
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

import requests


def _as_dt(value, tz: ZoneInfo) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(tz) if value.tzinfo else value.replace(tzinfo=tz)
    return datetime.combine(value, time.min, tzinfo=tz)


def _normalize_rrule_until(rrule_text: str, dtstart: datetime) -> str:
    if dtstart.tzinfo is None:
        return rrule_text

    def replace(match: re.Match[str]) -> str:
        prefix = match.group(1)
        value = match.group(2)
        if value.endswith("Z"):
            return match.group(0)

        if re.fullmatch(r"\d{8}", value):
            until = datetime.strptime(value, "%Y%m%d").replace(hour=23, minute=59, second=59, tzinfo=dtstart.tzinfo)
        elif re.fullmatch(r"\d{8}T\d{6}", value):
            until = datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=dtstart.tzinfo)
        elif re.fullmatch(r"\d{8}T\d{4}", value):
            until = datetime.strptime(value, "%Y%m%dT%H%M").replace(tzinfo=dtstart.tzinfo)
        else:
            return match.group(0)

        return f"{prefix}{until.astimezone(UTC):%Y%m%dT%H%M%SZ}"

    return re.sub(r"(UNTIL=)([^;:]+)", replace, rrule_text)


def collect(config: dict, today: datetime | None = None) -> dict:
    from dateutil.rrule import rrulestr
    from icalendar import Calendar

    urls = config.get("ical_urls", [])
    if not urls:
        return {"ok": False, "message": "google_calendar.json に ical_urls がありません。", "items": []}

    tz = ZoneInfo(config.get("timezone", "Asia/Tokyo"))
    base = today.astimezone(tz) if today else datetime.now(tz)
    start = datetime.combine(base.date(), time.min, tzinfo=tz)
    end = datetime.combine(base.date(), time.max, tzinfo=tz)
    items = []

    for url in urls:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.content)
        for event in cal.walk("VEVENT"):
            dtstart = _as_dt(event.decoded("DTSTART"), tz)
            dtend = _as_dt(event.decoded("DTEND", event.decoded("DTSTART")), tz)
            starts = [dtstart]
            if event.get("RRULE"):
                rrule_text = event.get("RRULE").to_ical().decode()
                rrule_text = _normalize_rrule_until(rrule_text, dtstart)
                rule = rrulestr(rrule_text, dtstart=dtstart)
                starts = list(rule.between(start, end, inc=True))
            for occurrence in starts:
                occurrence_end = occurrence + (dtend - dtstart)
                if occurrence < end and occurrence_end > start:
                    items.append(
                        {
                            "summary": str(event.get("SUMMARY", "予定")),
                            "start": occurrence.isoformat(),
                            "end": occurrence_end.isoformat(),
                        }
                    )

    items.sort(key=lambda x: x["start"])
    return {"ok": True, "items": items}
