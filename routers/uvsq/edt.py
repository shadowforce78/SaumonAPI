from fastapi import APIRouter
import json
import requests
import datetime
from bs4 import BeautifulSoup
from AI import format_edt_ia

router = APIRouter(prefix="/uvsq", tags=["UVSQ"])


@router.get("/edt/{classe}+{start_date}+{end_date}")
def read_edt(classe: str, start_date: str, end_date: str):
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

        response = requests.post(endpoint, headers=headers, data=body)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 500:
            print(f"Erreur serveur : {response.text}")
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
        cours_format_ia = (
            cours_format_ia.replace("```json", "").replace("```", "").strip()
        )
        # Parse the string as JSON
        formatted_json = json.loads(cours_format_ia)
        # Return the parsed JSON (FastAPI will handle the JSON formatting)
        return formatted_json
    except json.JSONDecodeError:
        return {"error": "Failed to parse response as JSON"}


@router.get("/classe/{q}")
def search_classe(q: str):
    url = "https://edt.iut-velizy.uvsq.fr/Home/ReadResourceListItems"
    params = {
        "myResources": "false",
        "searchTerm": q,
        "pageSize": "15",
        "pageNumber": "1",
        "resType": "103",
    }
    response = requests.get(url, params=params)
    return response.json()