import logging
from datetime import date

import resend

import config

logger = logging.getLogger(__name__)


def _build_subject() -> str:
    week_number = date.today().isocalendar()[1]
    return f"{config.EMAIL_SUBJECT_PREFIX} — Semana {week_number} | João Paulo"


def send_report(body: str) -> None:
    resend.api_key = config.RESEND_API_KEY
    subject = _build_subject()

    logger.info(f"Sending via Resend from {config.EMAIL_FROM} to {config.EMAIL_RECIPIENT}")

    try:
        response = resend.Emails.send({
            "from": config.EMAIL_FROM,
            "to": config.EMAIL_RECIPIENT,
            "subject": subject,
            "html": body,
        })
        logger.info(f"Email sent | id={response['id']} | Subject: {subject}")
    except Exception as e:
        logger.error(f"Resend error: {e}")
        raise RuntimeError(f"Failed to send email via Resend: {e}")
