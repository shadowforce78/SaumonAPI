from fastapi import FastAPI
import json
import requests
from bs4 import BeautifulSoup
import datetime


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
    return cours


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
def read_item(id: str, password: str):
    if not id.isdigit():
        return {"error": "L'identifiant doit être un chiffre"}

    class BulletinClient:
        def __init__(self, username: str, password: str):
            self.username = username
            self.password = password
            self.session = requests.Session()

        def __del__(self):
            # Ensure session is properly closed
            self.session.close()

        def login(self):
            try:
                # 1. Gather the cookies
                url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
                response = self.session.post(url, timeout=10)
                response.raise_for_status()

                # 2. Gather JWT token
                url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                token = soup.find("input", {"name": "execution"})
                if not token:
                    return {"error": "Could not obtain authentication token"}
                token = token["value"]

                # 3. Login
                payload = {
                    "username": self.username,
                    "password": self.password,
                    "execution": token,
                    "_eventId": "submit",
                    "geolocation": "",
                }
                response = self.session.post(url, data=payload, timeout=10)
                response.raise_for_status()
                
            except requests.RequestException as e:
                return {"error": f"Connection error: {str(e)}"}

        def fetch_datas(self):
            try:
                url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
                headers = {
                    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                }

                response = self.session.post(url, headers=headers, timeout=10)
                response.raise_for_status()
                json_data = response.text.replace("\n", "")
                return json.loads(json_data)
                
            except requests.RequestException as e:
                return {"error": f"Connection error: {str(e)}"}
            except json.JSONDecodeError:
                return {"error": "Invalid response from server"}

    try:
        client = BulletinClient(username=id, password=password)
        login_result = client.login()
        if isinstance(login_result, dict) and "error" in login_result:
            return login_result
            
        data = client.fetch_datas()
        if isinstance(data, dict) and "redirect" in data:
            return {"error": "Identifiants invalides"}
        return data
        
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    finally:
        if 'client' in locals():
            del client
