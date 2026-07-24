from __future__ import annotations

import os

import requests


WEATHER_CODE = {
    0: "快晴",
    1: "晴れ",
    2: "一部くもり",
    3: "くもり",
    45: "霧",
    48: "霧氷",
    51: "弱い霧雨",
    53: "霧雨",
    55: "強い霧雨",
    61: "弱い雨",
    63: "雨",
    65: "強い雨",
    71: "弱い雪",
    73: "雪",
    75: "強い雪",
    80: "弱いにわか雨",
    81: "にわか雨",
    82: "強いにわか雨",
    95: "雷雨",
}


def collect(config: dict) -> dict:
    lat = os.getenv("WEATHER_LATITUDE") or config.get("latitude")
    lon = os.getenv("WEATHER_LONGITUDE") or config.get("longitude")
    if lat is None or lon is None:
        return {"ok": False, "message": "WEATHER_LATITUDE/WEATHER_LONGITUDE がありません。"}

    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": config.get("timezone", "Asia/Tokyo"),
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 1,
    }
    resp = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=30)
    resp.raise_for_status()
    daily = resp.json()["daily"]
    code = daily["weather_code"][0]
    return {
        "ok": True,
        "location": config.get("label", "天気"),
        "date": daily["time"][0],
        "condition": WEATHER_CODE.get(code, f"天気コード {code}"),
        "temp_max": daily["temperature_2m_max"][0],
        "temp_min": daily["temperature_2m_min"][0],
        "precipitation_probability": daily["precipitation_probability_max"][0],
    }
