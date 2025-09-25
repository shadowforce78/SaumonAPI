from fastapi import APIRouter
import json
import requests
import datetime
from bs4 import BeautifulSoup
from AI import format_edt_ia

router = APIRouter(prefix="/uvsq", tags=["UVSQ"])


# @router.get("/edt/{classe}+{start_date}+{end_date}")
# def read_edt(classe: str, start_date: str, end_date: str):
#     # --- Configuration API ---
#     endPointUrl = "https://edt.iut-velizy.uvsq.fr/Home/GetCalendarData"

#     headers = {
#         "accept": "application/json, text/javascript, */*; q=0.01",
#         "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
#         "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
#     }

#     def make_body(start_date, end_date, federationIds):
#         # FederationIds to array
#         federationIds = [federationIds]
#         body = {
#             "start": start_date,
#             "end": end_date,
#             "resType": 103,
#             "calView": "agendaWeek",
#             "federationIds": federationIds,
#             "colourScheme": 3,
#         }
#         return body

#     def format_events(events):
#         formatted_data = {}

#         for event in events:
#             start_time = datetime.datetime.fromisoformat(event["start"])
#             end_time = datetime.datetime.fromisoformat(event["end"])

#             event_info = {
#                 "ID": event["id"],  # Ajouter l'ID de l'événement
#                 "Début": start_time.strftime("%H:%M"),
#                 "Fin": end_time.strftime("%H:%M"),
#                 "Description": event["description"]
#                 .replace("<br />", "\n")
#                 .replace("&39;", "'")
#                 .strip(),
#                 "Professeur(s)": event["description"].split("<br />")[0],
#                 "Module(s)": (
#                     ", ".join(event["modules"]) if event["modules"] else "Non spécifié"
#                 ),
#                 "Type": event["eventCategory"],
#                 "Site": ", ".join(event["sites"]) if event["sites"] else "Non spécifié",
#                 "Couleur": event["backgroundColor"],
#             }

#             date_str = start_time.strftime("%Y-%m-%d")
#             if date_str not in formatted_data:
#                 formatted_data[date_str] = []

#             formatted_data[date_str].append(event_info)

#         return formatted_data

#     def fetch_event_details(event_id):
#         """
#         Récupère les détails d'un événement donné son ID.
#         """
#         endpoint = "https://edt.iut-velizy.uvsq.fr/Home/GetSideBarEvent"
#         body = {"eventId": event_id}

#         response = requests.post(endpoint, headers=headers, data=body)
#         if response.status_code == 200:
#             return json.loads(response.text)
#         elif response.status_code == 500:
#             print(f"Erreur serveur : {response.text}")
#             return None
#         else:
#             print(
#                 f"Erreur lors de la récupération des détails de l'événement {event_id}: {response.status_code}"
#             )
#             return None

#     def fetch_and_format_data(start_date, end_date, class_name):
#         body = make_body(start_date, end_date, class_name)
#         response = requests.post(endPointUrl, headers=headers, data=body)
#         formatted_response = json.loads(response.text)
#         return format_events(formatted_response)

#     data = fetch_and_format_data(start_date, end_date, classe)
#     cours = []
#     for i in data:
#         for j in range(len(data[i])):
#             cours.append(fetch_event_details(data[i][j]["ID"]))
#     cours_format_ia = format_edt_ia(json.dumps(cours))

#     # Parse the string as JSON and return it directly
#     try:
#         # Remove the markdown code block symbols if present
#         cours_format_ia = (
#             cours_format_ia.replace("```json", "").replace("```", "").strip()
#         )
#         # Parse the string as JSON
#         formatted_json = json.loads(cours_format_ia)
#         # Return the parsed JSON (FastAPI will handle the JSON formatting)
#         return formatted_json
#     except json.JSONDecodeError:
#         return {"error": "Failed to parse response as JSON"}

links = {
        "INF1-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-NM2ABGDV5957/schedule.ics",
        "INF1-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-CU2JFTWC5958/schedule.ics",
        "INF1-B1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-DU2XQKER5960/schedule.ics",
        "INF1-B2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-VW2KSGLE5961/schedule.ics",
        "INF1-C1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-LD2VKATP5963/schedule.ics",
        "INF1-C2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-BG2EPJUY5964/schedule.ics",
        "INF2-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-QY2TXVVR5966/schedule.ics",
        "INF2-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-AJ2PMMSQ5967/schedule.ics",
        "INF2-B1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-CH2ALWCJ5968/schedule.ics",
        "INF2-B2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-NJ2HYPWU5969/schedule.ics",
        "INF2-FA": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-EP2CETAY5970/schedule.ics",
        "INF2-FI-A": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-FF2LEQYM5972/schedule.ics",
        "INF2-FI-B": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-SN2PGVBC5973/schedule.ics",
        "INF3-FA-A": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-KM2BSDSE5975/schedule.ics",
        "INF3-FA-B": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-FD2MLGKS5976/schedule.ics",
        "INF3-FI-A": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-LU2GUCAK5978/schedule.ics",
        "INF3-FI-B": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-JQ2EKUUB5979/schedule.ics",
        "MMI1-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-QJ2DMFYC5987/schedule.ics",
        "MMI1-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-PW2GUKMM5988/schedule.ics",
        "MMI1-B1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-HN2CHYNX5990/schedule.ics",
        "MMI1-B2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-QW2SJTJH5991/schedule.ics",
        "MMI2-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-QS2QEJVB5994/schedule.ics",
        "MMI2-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-EG2LDXAM5995/schedule.ics",
        "MMI2-B1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-AE2BGJHX5997/schedule.ics",
        "MMI2-B2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-TM2VJCBU5998/schedule.ics",
        "MMI3_GR1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-VC2XWEYV19912/schedule.ics",
        "MMI3_GR2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-CY2PNYVB19913/schedule.ics",
        "MMI3-FA-CN-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-CC2LTGMX6000/schedule.ics",
        "MMI3-FA-CN-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-HW2LKCBM6001/schedule.ics",
        "MMI3-FA-DW-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-TS2PGRAD6003/schedule.ics",
        "MMI3-FA-DW-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-KL2GMWYW6004/schedule.ics",
        "MMI3-FI-CN-A1": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-EB2URAPF6006/schedule.ics",
        "MMI3-FI-CN-A2": "https://celcat.rambouillet.iut-velizy.uvsq.fr/cal/ical/G1-JP2NSAYC6007/schedule.ics",
    }

@router.get("/edt/ics/{q}")
def get_raw_ics(q: str):
    if q in links:
        url = links[q]
        response = requests.get(url)
        return {"ics": response.text}
    else:
        return {"error": "Classe non trouvée"}


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
