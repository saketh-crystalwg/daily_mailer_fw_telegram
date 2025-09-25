import imaplib
import email
import os
from datetime import datetime, timedelta, timezone
import email.utils
import asyncio
from telegram import Bot
import logging
import nest_asyncio

# Gmail login (use App Password, not your normal password)
EMAIL = "andreicrystalwg2@gmail.com"
APP_PASSWORD = "szem lcqz trcg bhwp"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

async def send_files_to_telegram(files):
    # ----------------- CONFIG ----------------- #
    TELEGRAM_TOKEN = "8136460878:AAFvL8CYVaAnZx7srn8Yuwy0HQkERtLZlDc"
    CHAT_ID = "-4524311273"  # Telegram chat ID

    # ----------------- LOGGING ----------------- #
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    """
    Send a list of files (images, PDFs, etc.) to Telegram.
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    for file_path in files:
        try:
            with open(file_path, 'rb') as f:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    await bot.send_photo(chat_id=CHAT_ID, photo=f)
                else:
                    await bot.send_document(chat_id=CHAT_ID, document=f)
            logging.info(f"Sent {file_path} to Telegram")
        except Exception as e:
            logging.error(f"Failed to send {file_path}: {e}")



def download_fw_attachments():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox")

    # Fetch emails with subject starting with "FW: Executive Summary"
    status, messages = mail.search(None, '(SUBJECT "FW: Executive Summary")')
    email_ids = messages[0].split()

    print(f"Found {len(email_ids)} FW emails")

    now = datetime.now(timezone.utc)  # make 'now' timezone-aware in UTC
    time_threshold = now - timedelta(minutes=1440) #30

    for e_id in email_ids[-10:]:
        status, data = mail.fetch(e_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Parse the email's "Date" header
        email_date = email.utils.parsedate_to_datetime(msg["Date"])

        # Convert to UTC if it has timezone
        if email_date.tzinfo:
            email_date = email_date.astimezone(timezone.utc)
        else:
            email_date = email_date.replace(tzinfo=timezone.utc)

        # Skip emails older than 30 minutes
        if email_date < time_threshold:
            continue

        print("Subject:", msg["subject"], "| Date:", email_date)

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if filename:
                filepath = os.path.join("./", filename)  # save in root dir
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print("Downloaded:", filepath)

    mail.logout()

if __name__ == "__main__":
    download_fw_attachments()
    files_to_send = ["Executive Summary.pdf"]

    
    nest_asyncio.apply()
    asyncio.run(send_files_to_telegram(files_to_send))