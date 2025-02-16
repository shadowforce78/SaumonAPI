from fastapi import FastAPI
import json
import requests
from bs4 import BeautifulSoup
import datetime
from AI import format_edt_ia

class BulletinClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        # 1. Gather the cookies
        url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
        self.session.post(url)

        # 2. Gather JWT token
        url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
        response = self.session.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        token = soup.find("input", {"name": "execution"})["value"]

        # 3. Login
        url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
        payload = {
            "username": self.username,
            "password": self.password,
            "execution": token,
            "_eventId": "submit",
            "geolocation": "",
        }
        self.session.post(url, data=payload)

    def fetch_datas(self):
        url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
        headers = {
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        response = self.session.post(url, headers=headers)
        json_data = response.text.replace("\n", "")
        return json.loads(json_data)

    def fetch_releve(self, semestre):
        url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php"
        params = {
            "q": "relevéEtudiant",
            "semestre": semestre
        }
        headers = {
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        
        response = self.session.get(url, params=params, headers=headers)
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {"error": "Impossible de décoder la réponse JSON"}
        return {"error": f"Erreur {response.status_code}"}

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur mon API !"}


@app.get("/uvsq/edt/{classe}+{start_date}+{end_date}")
def read_item(classe: str, start_date: str, end_date: str):
    # --- Configuration API ---
    endPointUrl = "https://edt.iut-velizy.uvsq.fr/Home/GetCalendarData"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    def make_body(start_date, end_date, federationIds):

        # FederationIds to array
        federationIds = [federationIds]
        body = {
            "start": start_date,
            "end": end_date,
            "resType": 103,
            "calView": "agendaWeek",
            "federationIds": federationIds,
            "colourScheme": 3,
        }
        return body

    def format_events(events):
        formatted_data = {}

        for event in events:
            start_time = datetime.datetime.fromisoformat(event["start"])
            end_time = datetime.datetime.fromisoformat(event["end"])

            event_info = {
                "ID": event["id"],  # Ajouter l'ID de l'événement
                "Début": start_time.strftime("%H:%M"),
                "Fin": end_time.strftime("%H:%M"),
                "Description": event["description"]
                .replace("<br />", "\n")
                .replace("&39;", "'")
                .strip(),
                "Professeur(s)": event["description"].split("<br />")[0],
                "Module(s)": (
                    ", ".join(event["modules"]) if event["modules"] else "Non spécifié"
                ),
                "Type": event["eventCategory"],
                "Site": ", ".join(event["sites"]) if event["sites"] else "Non spécifié",
                "Couleur": event["backgroundColor"],
            }

            date_str = start_time.strftime("%Y-%m-%d")
            if date_str not in formatted_data:
                formatted_data[date_str] = []

            formatted_data[date_str].append(event_info)

        return formatted_data

    def fetch_event_details(event_id):
        """
        Récupère les détails d'un événement donné son ID.
        """
        endpoint = "https://edt.iut-velizy.uvsq.fr/Home/GetSideBarEvent"
        body = {"eventId": event_id}

        # print(f"Fetching details for event ID: {event_id}")
        response = requests.post(endpoint, headers=headers, data=body)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 500:
            print(
                f"Erreur serveur : {response.text}"
            )  # Ou un autre attribut contenant les détails
            return None
        else:
            print(
                f"Erreur lors de la récupération des détails de l'événement {event_id}: {response.status_code}"
            )
            return None

    def fetch_and_format_data(start_date, end_date, class_name):
        body = make_body(start_date, end_date, class_name)
        response = requests.post(endPointUrl, headers=headers, data=body)
        formatted_response = json.loads(response.text)
        return format_events(formatted_response)

    data = fetch_and_format_data(start_date, end_date, classe)
    cours = []
    for i in data:
        for j in range(len(data[i])):
            cours.append(fetch_event_details(data[i][j]["ID"]))
    cours_format_ia = format_edt_ia(json.dumps(cours))
    
    # Parse the string as JSON and return it directly
    try:
        # Remove the markdown code block symbols if present
        cours_format_ia = cours_format_ia.replace("```json", "").replace("```", "").strip()
        # Parse the string as JSON
        formatted_json = json.loads(cours_format_ia)
        # Return the parsed JSON (FastAPI will handle the JSON formatting)
        return formatted_json
    except json.JSONDecodeError:
        return {"error": "Failed to parse response as JSON"}


@app.get("/uvsq/classe/{q}")
def read_item(q: str):

    url = "https://edt.iut-velizy.uvsq.fr/Home/ReadResourceListItems"
    params = {
        "myResources": "false",
        "searchTerm": q,  # q est une variable contenant la valeur de recherche
        "pageSize": "15",
        "pageNumber": "1",
        "resType": "103",
    }
    response = requests.get(url, params=params)
    return response.json()


@app.get("/uvsq/bulletin/{id}+{password}")
#TODO : Query credentials instead of path parameters
def read_item(id: str, password: str):
    if not id.isdigit():
        return {"error": "L'identifiant doit être un chiffre"}
    
    import base64
    try:
        decoded_password = base64.b64decode(password).decode('utf-8')
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

@app.get("/uvsq/bulletin/releve/{id}+{password}+{semestre}")
def get_releve(id: str, password: str, semestre: str):
    if not id.isdigit():
        return {"error": "L'identifiant doit être un chiffre"}
    
    if not semestre.isdigit():
        return {"error": "Le semestre doit être un chiffre"}
    
    import base64
    try:
        decoded_password = base64.b64decode(password).decode('utf-8')
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
