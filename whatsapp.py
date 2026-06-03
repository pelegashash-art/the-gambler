import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
RECIPIENT = os.getenv("WHATSAPP_RECIPIENT")
API_URL = f"https://graph.facebook.com/v25.0/{PHONE_ID}/messages"

def send_message(text: str) -> bool:
    """Send a WhatsApp text message. Returns True on success."""
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT,
        "type": "text",
        "text": {"body": text, "preview_url": False}
    }
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=15)
    if resp.status_code == 200:
        print(f"[WhatsApp] Sent OK ({len(text)} chars)")
        return True
    else:
        print(f"[WhatsApp] Error {resp.status_code}: {resp.text}")
        return False

def send_long_message(text: str, max_chars: int = 4000) -> bool:
    """Split and send long messages in chunks."""
    if len(text) <= max_chars:
        return send_message(text)

    # Split at separator lines
    parts = text.split("━━━━━━━━━━━━━━━━━━")
    chunk = ""
    success = True
    for part in parts:
        if len(chunk) + len(part) < max_chars:
            chunk += "━━━━━━━━━━━━━━━━━━\n" + part if chunk else part
        else:
            if chunk:
                success = send_message(chunk) and success
            chunk = part
    if chunk:
        success = send_message(chunk) and success
    return success
