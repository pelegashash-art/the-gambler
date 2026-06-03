import os
import requests
from dotenv import load_dotenv

load_dotenv()

import json
from pathlib import Path

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
API_URL = f"https://graph.facebook.com/v25.0/{PHONE_ID}/messages"
RECIPIENTS_FILE = Path("data/recipients.json")


def get_recipients() -> list[str]:
    """Load recipients from file, fallback to env var."""
    if RECIPIENTS_FILE.exists():
        numbers = json.loads(RECIPIENTS_FILE.read_text())
        if numbers:
            return numbers
    default = os.getenv("WHATSAPP_RECIPIENT", "")
    return [default] if default else []


def send_to(number: str, text: str) -> bool:
    """Send a WhatsApp text message to a specific number."""
    payload = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {"body": text, "preview_url": False}
    }
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=15)
    if resp.status_code == 200:
        print(f"[WhatsApp] Sent to {number} OK ({len(text)} chars)")
        return True
    else:
        print(f"[WhatsApp] Error {resp.status_code} for {number}: {resp.text}")
        return False


def send_message(text: str) -> bool:
    """Send to all recipients."""
    recipients = get_recipients()
    if not recipients:
        print("[WhatsApp] No recipients configured!")
        return False
    return all(send_to(number, text) for number in recipients)


def send_long_message(text: str, max_chars: int = 4000) -> bool:
    """Split and send long messages in chunks to all recipients."""
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
