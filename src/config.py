from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str | Path, default: Any = None) -> Any:
    file_path = ROOT / path if not isinstance(path, Path) or not path.is_absolute() else path
    if not file_path.exists():
        return default
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def config(name: str, default: Any = None) -> Any:
    return load_json(Path("config") / f"{name}.json", default)
