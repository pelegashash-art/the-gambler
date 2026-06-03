import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("WHATSAPP_TOKEN")
phone_id = os.getenv("WHATSAPP_PHONE_ID")
recipient = os.getenv("WHATSAPP_RECIPIENT")

url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"

payload = {
    "messaging_product": "whatsapp",
    "to": recipient,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {"code": "en_US"}
    }
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print("Status:", response.status_code)
print("Response:", response.json())
