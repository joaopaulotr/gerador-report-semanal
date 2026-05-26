import os
import json
from dotenv import load_dotenv

load_dotenv()


def get_required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value


OPENAI_API_KEY = get_required("OPENAI_API_KEY")
GMAIL_USER = get_required("GMAIL_USER")
GMAIL_APP_PASSWORD = get_required("GMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = get_required("EMAIL_RECIPIENT")
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", "Relatório Semanal")
GDRIVE_REPORTS_FOLDER_NAME = os.getenv("GDRIVE_REPORTS_FOLDER_NAME", "Reports")

_service_account_raw = get_required("GOOGLE_SERVICE_ACCOUNT_JSON")
try:
    SERVICE_ACCOUNT_INFO = json.loads(_service_account_raw)
except json.JSONDecodeError as e:
    raise EnvironmentError(f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}")
