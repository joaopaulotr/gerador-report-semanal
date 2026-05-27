import logging
from datetime import date
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _build_service():
    creds = service_account.Credentials.from_service_account_info(
        config.SERVICE_ACCOUNT_INFO, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def _find_folder(service, name: str, parent_id: str = None) -> Optional[str]:
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    result = service.files().list(q=query, fields="files(id, name)").execute()
    files = result.get("files", [])
    return files[0]["id"] if files else None


def _find_file(service, name: str, parent_id: str) -> Optional[str]:
    query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    result = service.files().list(q=query, fields="files(id, name)").execute()
    files = result.get("files", [])
    return files[0]["id"] if files else None


def _download_file(service, file_id: str) -> str:
    content = service.files().get_media(fileId=file_id).execute()
    return content.decode("utf-8")


def get_weekly_report() -> Optional[str]:
    today = date.today()
    week_number = today.isocalendar()[1]
    year = today.year
    filename = f"Semana{week_number}.md"

    logger.info(f"Looking for: {filename} (year {year})")

    try:
        service = _build_service()

        reports_folder_id = _find_folder(service, config.GDRIVE_REPORTS_FOLDER_NAME)
        if not reports_folder_id:
            logger.error(f"Folder '{config.GDRIVE_REPORTS_FOLDER_NAME}' not found in Drive")
            return None

        year_folder_id = _find_folder(service, str(year), parent_id=reports_folder_id)
        if not year_folder_id:
            logger.error(f"Year folder '{year}' not found inside '{config.GDRIVE_REPORTS_FOLDER_NAME}'")
            return None

        file_id = _find_file(service, filename, parent_id=year_folder_id)
        if not file_id:
            logger.error(f"File '{filename}' not found in year folder '{year}'")
            return None

        content = _download_file(service, file_id)
        logger.info(f"File '{filename}' downloaded successfully ({len(content)} chars)")
        return content

    except HttpError as e:
        logger.error(f"Google Drive API error: {e}")
        return None
