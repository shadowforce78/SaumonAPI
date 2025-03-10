from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI")


def format_edt_ia(datajson):

    format = """
        "Date": "",
        "Heure": "",
        "Matière": ,
        "Personnel": ,
        "Groupe": "",
        "Salle": "",
        "Catégorie d’événement": "",
        "Remarques" : ""
        """

    prompt = (
        "Reorganise les données suivantes en un tableau lisible :"
        + datajson
        + " , je ne veux que du json brut au format suivant :"
        + format
    )

    client = genai.Client(api_key=gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
    )

    return response.text
