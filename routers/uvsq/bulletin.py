from fastapi import APIRouter
import base64
from services.bulletin_client import BulletinClient

router = APIRouter(prefix="/uvsq/bulletin", tags=["UVSQ Bulletins"])


@router.get("/{id}+{password}")
def get_bulletin(id: str, password: str):
    """
    Récupère les informations du bulletin d'un étudiant
    """
    if not id.isdigit():
        return {"error": "L'identifiant doit être un chiffre"}

    try:
        decoded_password = base64.b64decode(password).decode("utf-8")
    except:
        return {"error": "Le mot de passe a mal été encodé"}

    username = id
    password = decoded_password  # Utilisation du mot de passe décodé
    client = BulletinClient(username=username, password=password)
    client.login()
    data = client.fetch_datas()

    if "redirect" in data:
        return {"error": "Identifiants invalides"}
    else:
        return data


@router.get("/releve/{id}+{password}+{semestre}")
def get_releve(id: str, password: str, semestre: str):
    """
    Récupère le relevé de notes d'un étudiant pour un semestre donné
    """
    if not id.isdigit():
        return {"error": "L'identifiant doit être un chiffre"}

    if not semestre.isdigit():
        return {"error": "Le semestre doit être un chiffre"}

    try:
        decoded_password = base64.b64decode(password).decode("utf-8")
    except:
        return {"error": "Le mot de passe a mal été encodé"}

    client = BulletinClient(username=id, password=decoded_password)
    client.login()

    # Vérifier que la connexion a réussi
    initial_data = client.fetch_datas()
    if "redirect" in initial_data:
        return {"error": "Identifiants invalides"}

    # Récupérer le relevé
    return client.fetch_releve(semestre)