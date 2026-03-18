import requests
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def rechercher_voitures(query):
    url = f"https://api.leboncoin.fr/finder/search"
    
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "keywords": query,
        "category": "2"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print("Erreur API")
        return []

    data = response.json()
    return data.get("ads", [])

def filtrer(annonce):
    try:
        prix = annonce.get("price", [0])[0]
        km = int(annonce["attributes"].get("mileage", "0").split()[0])
        annee = int(annonce["attributes"].get("regdate", 0))
        titre = annonce.get("subject", "")
        lien = "https://www.leboncoin.fr" + annonce.get("url", "")

        # 🔥 tes règles
        if prix > 5000:
            return None
        if km > 150000:
            return None
        if annee < 2010:
            return None

        message = f"""
🚗 {titre}
💰 {prix}€
📏 {km} km
📅 {annee}
🔗 {lien}
"""

        return message

    except:
        return None

# 🔎 recherches
recherches = [
    "toyota yaris",
    "renault clio 4",
    "volkswagen polo",
    "hyundai i20",
    "skoda fabia",
    "ford fiesta",
    "citroen c3"
]

for recherche in recherches:
    annonces = rechercher_voitures(recherche)

    for annonce in annonces[:5]:
        message = filtrer(annonce)
        if message:
            envoyer_telegram(message)
