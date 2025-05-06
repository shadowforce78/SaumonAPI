from fastapi import FastAPI
import json
import requests
from bs4 import BeautifulSoup
import datetime
from AI import format_edt_ia
import base64
import re


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
        params = {"q": "relevéEtudiant", "semestre": semestre}
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
        cours_format_ia = (
            cours_format_ia.replace("```json", "").replace("```", "").strip()
        )
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
# TODO : Query credentials instead of path parameters
def read_item(id: str, password: str):
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


@app.get("/uvsq/bulletin/releve/{id}+{password}+{semestre}")
def get_releve(id: str, password: str, semestre: str):
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


@app.get("/scans/info/{name}")
def get_scan_info(name: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    url = "https://anime-sama.fr/catalogue/" + name
    response = requests.get(url, headers=headers)
    html_content = response.text

    # Extraire les informations de la page
    try:
        # Créer le parser BeautifulSoup pour extraire des informations basiques
        soup = BeautifulSoup(html_content, "html.parser")

        # Extraire le titre
        titre_element = soup.find("h4", {"id": "titreOeuvre"})
        titre = titre_element.text if titre_element else "Non disponible"

        # Extraire le titre alternatif
        titre_alter_element = soup.find("h2", {"id": "titreAlter"})
        titre_alter = (
            titre_alter_element.text if titre_alter_element else "Non disponible"
        )

        # Extraire l'image de couverture
        image_element = soup.find("img", {"id": "coverOeuvre"})
        image_url = image_element["src"] if image_element else "Non disponible"

        # Extraire le synopsis
        synopsis_element = soup.find_all("p", class_="text-sm text-gray-400 mt-2")
        synopsis = synopsis_element[0].text if synopsis_element else "Non disponible"

        # Extraire les genres
        genres_element = soup.find("a", class_="text-sm text-gray-300 mt-2")
        genres = genres_element.text if genres_element else "Non disponible"

        # Extraire les informations sur l'avancement
        avancement_element = soup.find(
            lambda tag: tag.name == "p" and "Avancement :" in tag.text
        )
        avancement = (
            avancement_element.find("a").text
            if avancement_element
            else "Non disponible"
        )

        # Extraire les informations sur la correspondance
        correspondance_element = soup.find(
            lambda tag: tag.name == "p" and "Correspondance :" in tag.text
        )
        correspondance = (
            correspondance_element.find("a").text
            if correspondance_element
            else "Non disponible"
        )

        # Extraire les saisons d'anime à partir des appels à panneauAnime()

        anime_disponibles = []
        anime_pattern = r'panneauAnime\("([^"]+)",\s*"([^"]+)"\);'
        anime_matches = re.findall(anime_pattern, html_content)
        for match in anime_matches:
            nom, url = match
            anime_disponibles.append({"nom": nom, "url": url})

        # Retirer le premier élément de la liste
        if len(anime_disponibles) > 0:
            anime_disponibles.pop(0)

        # Extraire les types de scans à partir des appels à panneauScan()
        scans_disponibles = []
        scan_pattern = r'panneauScan\("([^"]+)",\s*"([^"]+)"\);'
        scan_matches = re.findall(scan_pattern, html_content)
        for match in scan_matches:
            nom, url = match
            scans_disponibles.append({"nom": nom, "url": url})

        # Retirer le premier élément de la liste
        if len(scans_disponibles) > 0:
            scans_disponibles.pop(0)

        # Construire la structure de réponse JSON
        scan_info = {
            "titre": titre,
            "titre_alternatif": titre_alter,
            "image_url": image_url,
            "synopsis": synopsis,
            "genres": genres,
            "avancement": avancement,
            "correspondance": correspondance,
            "contenu_disponible": {
                "anime": {
                    "disponible": len(anime_disponibles) > 0,
                    "saisons": anime_disponibles,
                },
                "manga": {
                    "disponible": len(scans_disponibles) > 0,
                    "types": scans_disponibles,
                },
            },
        }

        return scan_info

    except Exception as e:
        return {"error": f"Erreur lors de l'extraction des données : {str(e)}"}


@app.get("/scans/search/{query}")
def search_anime(query: str):
    """
    Effectue une recherche sur anime-sama.fr avec le terme spécifié

    Args:
        query: Le terme de recherche

    Returns:
        Les résultats de la recherche au format JSON
    """
    url = "https://anime-sama.fr/template-php/defaut/fetch.php"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Origin": "https://anime-sama.fr",
        "Referer": "https://anime-sama.fr/",
    }

    # Prépare les données POST
    data = {"query": query}

    try:
        # Exécute la requête POST
        response = requests.post(url, headers=headers, data=data)

        # Si la réponse est HTML, on extrait les informations
        if response.headers.get("content-type", "").startswith("text/html"):
            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Trouve tous les liens de résultats
            links = soup.find_all("a")
            for link in links:
                href = link.get("href")
                title = link.text.strip()

                # Vérifie si c'est une image dans le lien
                img = link.find("img")
                image_url = img.get("src") if img else None

                if href and title:
                    results.append({"titre": title, "url": href, "image": image_url})

            return {"query": query, "count": len(results), "results": results}

        # Si la réponse est déjà au format JSON
        elif response.headers.get("content-type", "").startswith("application/json"):
            return response.json()

        # Si on ne peut pas traiter la réponse
        else:
            return {
                "error": "Format de réponse non reconnu",
                "content-type": response.headers.get("content-type"),
                "text": response.text[:100],  # Premiers 100 caractères pour déboguer
            }

    except Exception as e:
        return {"error": f"Erreur lors de la recherche : {str(e)}"}
