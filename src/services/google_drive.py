from __future__ import annotations

import io
import json
import os
from pathlib import Path
from typing import Any


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if raw:
        info = json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    elif path:
        creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    else:
        raise RuntimeError("Google Drive credentials are not set")
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_files(folder_id: str, start_iso: str, end_iso: str, mime_prefix: str = "audio/") -> list[dict[str, Any]]:
    service = drive_service()
    query = (
        f"'{folder_id}' in parents and trashed=false "
        f"and createdTime >= '{start_iso}' and createdTime < '{end_iso}' "
        f"and mimeType contains '{mime_prefix}'"
    )
    resp = service.files().list(
        q=query,
        fields="files(id,name,mimeType,createdTime,modifiedTime)",
        orderBy="createdTime",
    ).execute()
    return resp.get("files", [])


def download_file(file_id: str, destination: str | Path) -> Path:
    from googleapiclient.http import MediaIoBaseDownload

    service = drive_service()
    request = service.files().get_media(fileId=file_id)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return destination
