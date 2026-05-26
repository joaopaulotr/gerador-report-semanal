import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

from src.drive_reader import get_weekly_report
from src.formatter import format_report
from src.sender import send_report


def main():
    logger.info("📂 Step 1/3 — Reading report from Google Drive")
    raw_content = get_weekly_report()

    if raw_content is None:
        logger.error("❌ Report file not found. Check Drive folder structure and service account permissions.")
        sys.exit(1)

    logger.info("🤖 Step 2/3 — Formatting report with GPT-4o")
    formatted = format_report(raw_content)

    logger.info("📧 Step 3/3 — Sending email via Gmail SMTP")
    send_report(formatted)

    logger.info("✅ Done — Weekly report sent successfully")


if __name__ == "__main__":
    main()
