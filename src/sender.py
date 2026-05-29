import logging
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import config

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _build_subject() -> str:
    week_number = date.today().isocalendar()[1]
    return f"{config.EMAIL_SUBJECT_PREFIX} — Semana {week_number} | João Paulo"


def send_report(body: str) -> None:
    subject = _build_subject()

    msg = MIMEMultipart()
    msg["From"] = config.GMAIL_USER
    msg["To"] = config.EMAIL_RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))

    logger.info(f"Connecting to {SMTP_HOST}:{SMTP_PORT}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            try:
                server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"Gmail authentication failed. Check GMAIL_USER and GMAIL_APP_PASSWORD. Error: {e}")
                raise RuntimeError(
                    f"Gmail authentication failed. Check GMAIL_USER and GMAIL_APP_PASSWORD. Error: {e}"
                )

            server.sendmail(config.GMAIL_USER, config.EMAIL_RECIPIENT, msg.as_string())
            logger.info(f"Email sent to {config.EMAIL_RECIPIENT} | Subject: {subject}")

    except smtplib.SMTPConnectError as e:
        logger.error(f"Could not connect to {SMTP_HOST}:{SMTP_PORT}. Error: {e}")
        raise RuntimeError(f"Could not connect to {SMTP_HOST}:{SMTP_PORT}. Error: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise RuntimeError(f"SMTP error: {e}")
