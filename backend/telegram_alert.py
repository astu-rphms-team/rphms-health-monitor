"""
Sends a Telegram message when a patient's vitals become CRITICAL.

Setup (see README for full steps):
1. Message @BotFather on Telegram, create a bot, copy the bot token.
2. Message your new bot once (any text), then visit:
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   to find your numeric chat id.
3. Put both values in backend/.env (see .env.example).

If the env vars are not set, alerts are still saved to the database and
shown on the dashboard - only the Telegram push is skipped. This means
the system still works for a demo even without Telegram configured.
"""

import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_telegram_alert(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[telegram] Skipped - TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=5,
        )
        if response.status_code == 200:
            return True
        print(f"[telegram] Failed: {response.status_code} {response.text}")
        return False
    except requests.RequestException as e:
        print(f"[telegram] Error sending alert: {e}")
        return False
