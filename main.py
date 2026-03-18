import requests
import os

# 🔐 Récupération des secrets
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    
    requests.post(url, data=data)

# 🔥 TEST (tu recevras ça sur Telegram)
envoyer_telegram("🔥 Bot Leboncoin connecté avec succès !")
