#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def send_webhook_alert(title, message, webhook_url=None):
    url = webhook_url or os.getenv("CINEGRADE_WEBHOOK_URL")
    if not url:
        print("Webhook URL not configured. Skipping remote notification.")
        return False
    
    payload = {
        "content": f"🎬 **{title}**\n{message}"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Webhook alert sent successfully.")
        return True
    except Exception as e:
        print(f"Failed to send webhook alert: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        send_webhook_alert(sys.argv[1], sys.argv[2])
