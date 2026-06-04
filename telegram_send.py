import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1003066187485")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_message(text: str) -> bool:
    """Send a message to the Telegram channel."""
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=15)
        if resp.status_code == 200:
            print(f"[Telegram] Sent OK ({len(text)} chars)")
            return True
        else:
            print(f"[Telegram] Error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Exception: {e}")
        return False


def send_long_message(text: str, max_chars: int = 4000) -> bool:
    """Split and send long messages in chunks."""
    if len(text) <= max_chars:
        return send_message(text)

    parts = text.split("━━━━━━━━━━━━━━━━")
    chunk = ""
    success = True
    for part in parts:
        if len(chunk) + len(part) < max_chars:
            chunk += "━━━━━━━━━━━━━━━━\n" + part if chunk else part
        else:
            if chunk:
                success = send_message(chunk) and success
            chunk = part
    if chunk:
        success = send_message(chunk) and success
    return success
