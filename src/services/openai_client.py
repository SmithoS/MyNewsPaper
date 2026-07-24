from __future__ import annotations

import os
from pathlib import Path


def _client():
    if not os.getenv("OPENAI_API_KEY"):
        return None
    from openai import OpenAI

    return OpenAI()


def summarize_text(text: str, system: str, model: str | None = None) -> str:
    client = _client()
    if not client:
        return "OPENAI_API_KEY が未設定のため要約をスキップしました。"

    response = client.chat.completions.create(
        model=model or os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4.1-mini"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text[:60000]},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def transcribe_audio(path: str | Path, model: str | None = None) -> str:
    client = _client()
    if not client:
        return ""

    with Path(path).open("rb") as audio:
        result = client.audio.transcriptions.create(
            model=model or os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"),
            file=audio,
        )
    return getattr(result, "text", "") or ""
