import requests
from bs4 import BeautifulSoup
import json
import re
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def envoyer_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram non configuré")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data, timeout=20)

# =========================
# CONFIGURATION PAR MODÈLE
# =========================
MODELES = {
    "yaris": {
        "recherche": "toyota yaris",
        "modele_nom": "Yaris",
        "annee_min": 2009,
        "annee_max": 2014,
        "prix_min": 4500,
        "prix_max": 5000,
        "revente_min": 7500,
        "revente_max": 8500,
        "km_max": 150000,
        "carburants": ["Essence", "Hybride", "Diesel"],
        "moteurs_ok": ["1.0", "1.3", "1.5 hybrid", "vvt-i", "hybrid"],
        "moteurs_interdits": [],
    },
    "clio4": {
        "recherche": "renault clio 4",
        "modele_nom": "Clio 4",
        "annee_min": 2013,
        "annee_max": 2015,
        "prix_min": 4800,
        "prix_max": 5200,
        "revente_min": 7500,
        "revente_max": 8500,
        "km_max": 150000,
        "carburants": ["Essence", "Diesel"],
        "moteurs_ok": ["0.9 tce 90", "1.2 16v 75", "0.9 tce", "1.2 16v"],
        "moteurs_interdits": ["1.2 tce 120"],
    },
    "polo": {
        "recherche": "volkswagen polo",
        "modele_nom": "Polo",
        "annee_min": 2011,
        "annee_max": 2015,
        "prix_min": 4500,
        "prix_max": 5000,
        "revente_min": 7000,
        "revente_max": 8200,
        "km_max": 150000,
        "carburants": ["Essence", "Diesel"],
        "moteurs_ok": ["1.0 mpi", "1.2 mpi", "mpi"],
        "moteurs_interdits": ["1.2 tsi", "1.4 tsi", "tsi"],
    },
    "i20": {
        "recherche": "hyundai i20",
        "modele_nom": "i20",
        "annee_min": 2012,
        "annee_max": 2015,
        "prix_min": 4200,
        "prix_max": 4800,
        "revente_min": 7000,
        "revente_max": 8000,
        "km_max": 150000,
        "carburants": ["Essence", "Diesel"],
        "moteurs_ok": ["1.2 mpi", "1.4 mpi", "mpi"],
        "moteurs_interdits": [],
    },
    "fabia": {
        "recherche": "skoda fabia",
        "modele_nom": "Fabia",
        "annee_min": 2011,
        "annee_max": 2015,
        "prix_min": 4200,
        "prix_max": 4800,
        "revente_min": 6800,
        "revente_max": 7800,
        "km_max": 150000,
        "carburants": ["Essence", "Diesel"],
        "moteurs_ok": ["1.0 mpi", "1.2 mpi", "mpi"],
        "moteurs_interdits": ["1.2 tsi", "1.4 tsi", "tsi"],
    },
    "fiesta": {
        "recherche": "ford fiesta",
        "modele_nom": "Fiesta",
        "annee_min": 2011,
        "annee_max": 2015,
        "prix_min": 3500,
        "prix_max": 5000,
        "revente_min": 6500,
        "revente_max": 8000,
        "km_max": 150000,
        "carburants": ["Essence", "Diesel"],
        "moteurs_ok": ["1.25", "1.4 essence"],
        "moteurs_interdits": ["ecoboost"],
    },
    "c3": {
        "recherche": "citroen c3",
        "modele_nom": "C3",
        "annee_min": 2011,
        "annee_max": 2015,
        "prix_min": 4000,
        "prix_max": 4800,
        "revente_min": 6500,
        "revente_max": 7800,
        "km_max": 150000,
        "carburants": ["Essence", "Diesel"],
        "moteurs_ok": ["1.4 vti", "1.6 vti", "vti"],
        "moteurs_interdits": ["1.2 puretech", "puretech", "1.6 thp", "thp"],
    }
}

MOTS_BONUS = [
    "urgent",
    "vend vite",
    "premier venu",
    "a saisir",
    "à saisir",
    "cause depart",
    "cause départ",
    "doit partir"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}

def nettoyer_km(valeur):
    if not valeur:
        return None
    chiffres = re.sub(r"[^\d]", "", str(valeur))
    return int(chiffres) if chiffres else None

def chercher_ads(obj):
    if isinstance(obj, dict):
        for cle, valeur in obj.items():
            if cle == "ads" and isinstance(valeur, list):
                return valeur
            resultat = chercher_ads(valeur)
            if resultat:
                return resultat
    elif isinstance(obj, list):
        for item in obj:
            resultat = chercher_ads(item)
            if resultat:
                return resultat
    return None

def recuperer_annonces(recherche):
    url = f"https://www.leboncoin.fr/recherche?category=2&text={recherche.replace(' ', '%20')}"
    response = requests.get(url, headers=HEADERS, timeout=20)
    print(f"\nRecherche : {recherche} | Code réponse : {response.status_code}")

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup.find_all("script"):
        contenu = script.string
        if not contenu:
            continue

        if "ads" in contenu:
            try:
                match = re.search(r'(\{.*"ads".*\})', contenu, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    annonces = chercher_ads(data)
                    if annonces:
                        return annonces
            except Exception:
                pass

    return []

def moteur_autorise(titre, regles):
    titre_lower = titre.lower()

    for mot in regles["moteurs_interdits"]:
        if mot.lower() in titre_lower:
            return False

    if regles["moteurs_ok"]:
        for mot in regles["moteurs_ok"]:
            if mot.lower() in titre_lower:
                return True
        return False

    return True

def regles_speciales(modele_key, carburant, km, titre):
    titre_lower = titre.lower()

    if modele_key == "clio4":
        if "1.2 tce 120" in titre_lower:
            return False

    if modele_key == "i20":
        if carburant == "Diesel" and km > 140000:
            return False

    if modele_key == "fiesta":
        if "ecoboost" in titre_lower:
            return False

    return True

def calculer_score(prix, km, annee, titre, marge_max):
    score = 0

    if marge_max >= 3000:
        score += 40
    elif marge_max >= 2500:
        score += 30
    elif marge_max >= 2000:
        score += 20
    else:
        score += 10

    if km <= 100000:
        score += 30
    elif km <= 130000:
        score += 20
    elif km <= 150000:
        score += 10

    if annee >= 2015:
        score += 20
    elif annee >= 2013:
        score += 15
    elif annee >= 2011:
        score += 10
    else:
        score += 5

    titre_lower = titre.lower()
    for mot in MOTS_BONUS:
        if mot in titre_lower:
            score += 10

    return score

annonces_interessantes = []
liens_vus = set()

for modele_key, regles in MODELES.items():
    annonces = recuperer_annonces(regles["recherche"])

    for annonce in annonces:
        titre = annonce.get("subject", "N/A")
        prix = annonce.get("price", ["N/A"])
        prix = prix[0] if isinstance(prix, list) and prix else prix

        try:
            prix_num = int(prix)
        except Exception:
            continue

        url_annonce = annonce.get("url", "N/A")
        if isinstance(url_annonce, str) and url_annonce.startswith("/"):
            url_annonce = "https://www.leboncoin.fr" + url_annonce

        if url_annonce in liens_vus:
            continue

        attrs = annonce.get("attributes", [])

        kilometrage = None
        annee = None
        carburant = "N/A"
        marque = "N/A"
        modele = "N/A"

        for attr in attrs:
            cle = attr.get("key", "")
            valeur = attr.get("value_label", attr.get("value", "N/A"))

            if cle == "brand":
                marque = valeur
            elif cle == "model":
                modele = valeur
            elif cle == "mileage":
                kilometrage = nettoyer_km(valeur)
            elif cle == "regdate":
                try:
                    annee = int(str(valeur))
                except Exception:
                    annee = None
            elif cle == "fuel":
                carburant = valeur

        if prix_num < regles["prix_min"] or prix_num > regles["prix_max"]:
            continue

        if kilometrage is None or kilometrage > regles["km_max"]:
            continue

        if annee is None or annee < regles["annee_min"] or annee > regles["annee_max"]:
            continue

        if carburant not in regles["carburants"]:
            continue

        if not moteur_autorise(titre, regles):
            continue

        if not regles_speciales(modele_key, carburant, kilometrage, titre):
            continue

        marge_min = regles["revente_min"] - prix_num
        marge_max = regles["revente_max"] - prix_num

        score = calculer_score(prix_num, kilometrage, annee, titre, marge_max)

        if marge_min < 1500:
            continue

        if score < 60:
            continue

        liens_vus.add(url_annonce)
        annonces_interessantes.append({
            "fiche_modele": regles["modele_nom"],
            "titre": titre,
            "marque": marque,
            "modele": modele,
            "prix": prix_num,
            "km": kilometrage,
            "annee": annee,
            "carburant": carburant,
            "revente_min": regles["revente_min"],
            "revente_max": regles["revente_max"],
            "marge_min": marge_min,
            "marge_max": marge_max,
            "score": score,
            "lien": url_annonce
        })

annonces_interessantes.sort(
    key=lambda x: (x["marge_max"], x["score"]),
    reverse=True
)

print("\n" + "=" * 100)
print(f"🔥 Annonces intéressantes : {len(annonces_interessantes)}")
print("=" * 100)

if not annonces_interessantes:
    print("Aucune annonce intéressante trouvée.")
else:
    for annonce in annonces_interessantes:
        print("🚗 Fiche modèle :", annonce["fiche_modele"])
        print("📝 Titre        :", annonce["titre"])
        print("🏷️ Marque/Modèle:", annonce["marque"], annonce["modele"])
        print("💰 Achat        :", annonce["prix"], "€")
        print("📈 Revente      :", annonce["revente_min"], "-", annonce["revente_max"], "€")
        print("💸 Marge        :", annonce["marge_min"], "-", annonce["marge_max"], "€")
        print("📏 Kilométrage  :", annonce["km"], "km")
        print("📅 Année        :", annonce["annee"])
        print("⛽ Carburant    :", annonce["carburant"])
        print("⭐ Score        :", annonce["score"])
        print("🔗 Lien         :", annonce["lien"])
        print("-" * 100)

        message = (
            f"🚗 {annonce['fiche_modele']}\n"
            f"📝 {annonce['titre']}\n"
            f"💰 Achat : {annonce['prix']} €\n"
            f"📈 Revente : {annonce['revente_min']} - {annonce['revente_max']} €\n"
            f"💸 Marge : {annonce['marge_min']} - {annonce['marge_max']} €\n"
            f"📏 {annonce['km']} km\n"
            f"📅 {annonce['annee']}\n"
            f"⛽ {annonce['carburant']}\n"
            f"⭐ Score : {annonce['score']}\n"
            f"🔗 {annonce['lien']}"
        )
        envoyer_telegram(message)
