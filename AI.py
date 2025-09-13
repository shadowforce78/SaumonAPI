"""Utilitaires d'appel au modèle Gemini pour le formatage EDT.

Ce module récupère la clé API depuis plusieurs noms possibles afin de
réduire les erreurs de configuration entre environnements (local / serveur / CI).
"""

from google import genai
from dotenv import load_dotenv
import os
from functools import lru_cache
from typing import Optional

# Charger le .env si présent (ne casse pas si absent)
load_dotenv()

POSSIBLE_KEY_NAMES = [
    "GEMINI",  # nom actuel dans le projet
    "GEMINI_API_KEY",  # nom classique
    "GOOGLE_GENAI_API_KEY",  # variante possible
    "GENAI_API_KEY",  # autre variante
]


def _find_api_key() -> Optional[str]:
    """Recherche la première variable d'environnement définie parmi les noms connus."""
    for name in POSSIBLE_KEY_NAMES:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """Retourne un client Gemini initialisé ou lève une erreur explicite.

    Utilise un cache pour éviter de recréer le client à chaque requête.
    """
    key = _find_api_key()
    if not key:
        raise RuntimeError(
            "Clé API Gemini manquante. Définis une des variables d'environnement: "
            + ", ".join(POSSIBLE_KEY_NAMES)
            + " (ex: GEMINI=ta_clef). Redémarre ensuite le service."
        )
    return genai.Client(api_key=key)


def format_edt_ia(datajson: str) -> str:
    """Formate les données EDT en JSON structurée via le modèle Gemini.

    Args:
        datajson: chaîne JSON brute représentant les cours collectés.
    Returns:
        Réponse textuelle du modèle (attendue JSON brut côté consommateur).
    Peut lever RuntimeError si la clé API est absente.
    """

    # Modèle de format attendu (laisser valeurs vides pour guidage)
    expected_format = (
        '{"Date": "", "Heure": "", "Matière": "", "Personnel": "", '
        '"Groupe": "", "Salle": "", "Catégorie d’événement": "", "Remarques": ""}'
    )

    prompt = (
        "Reorganise les données suivantes en un tableau lisible (un tableau JSON d'objets): "
        + datajson
        + " . Répond UNIQUEMENT par du JSON brut valide (UTF-8) avec le format des clés: "
        + expected_format
    )

    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
    )

    return response.text


if __name__ == "__main__":  # Petit test manuel possible
    try:
        print("Client Gemini initialisé:", bool(get_gemini_client()))
    except RuntimeError as e:
        print("[ERREUR]", e)
