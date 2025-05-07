from fastapi import APIRouter
import requests
from bs4 import BeautifulSoup
import re

router = APIRouter(tags=["Scans"])


@router.get("/scans/info/{name}")
def get_scan_info(name: str):
    """
    Récupère les informations d'un anime/manga par son nom
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    url = f"https://anime-sama.fr/catalogue/{name}"
    response = requests.get(url, headers=headers)
    html_content = response.text

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

        # Retirer la première entrée car elle est vide
        if len(anime_disponibles) > 0:
            anime_disponibles.pop(0)

        # Extraire les types de scans à partir des appels à panneauScan()
        scans_disponibles = []
        scan_pattern = r'panneauScan\("([^"]+)",\s*"([^"]+)"\);'
        scan_matches = re.findall(scan_pattern, html_content)
        for match in scan_matches:
            nom, url = match
            scans_disponibles.append({"nom": nom, "url": url})

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


@router.get("/scans/search/{query}")
def search_anime(query: str):
    """
    Effectue une recherche sur anime-sama.fr avec le terme spécifié
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
                    results.append(
                        {
                            "titre": title,
                            "url": href,
                            "image": image_url,
                            "name-for-info": href.rstrip("/").split("/")[-1],
                        }
                    )

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


@router.get("/scans/get_info_from_search/{query}")
def get_info_from_search(query: str):
    """
    Récupère les informations d'un anime/manga à partir de la recherche
    """
    search_result = search_anime(query)
    if "results" in search_result and len(search_result["results"]) > 0:
        first_result = search_result["results"][0]
        name_for_info = first_result["name-for-info"]
        return get_scan_info(name_for_info)
    else:
        return {"error": "Aucun résultat trouvé"}


@router.get("/scans/get_scan/{name}/{url:path}")
def get_scan(name: str, url: str):
    """
    Récupère les informations d'un scan à partir de son nom et de son URL
    Combine les fonctionnalités de get_scan_id et get_scans en un seul endpoint
    """
    # Base URL for anime-sama
    urlbase = "https://anime-sama.fr/catalogue/"

    # Remove leading and trailing slashes from URL parameter if present
    url = url.strip("/")

    # Construct the full URL - ensure no double slashes
    fullurl = f"{urlbase}{name}/{url}/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Étape 1: Faire la requête pour trouver l'ID du scan
    response = requests.get(fullurl, headers=headers)

    if response.status_code != 200:
        return {
            "error": f"Failed to access page, status code: {response.status_code}",
            "fullUrl": fullurl,
        }

    # Parse the response to find the scan ID
    soup = BeautifulSoup(response.text, "html.parser")
    html_content = response.text

    # Try multiple methods to find the scan ID
    id_scan = None

    # Method 1: Look for script tags with episodes.js?filever=
    script_tags = soup.find_all("script")
    for script in script_tags:
        if script.get("src") and "episodes.js?filever=" in script.get("src"):
            match = re.search(r"filever=(\d+)", script.get("src"))
            if match:
                id_scan = match.group(1)
                break

    # Method 2: Look for script tags containing episodes.js?filever= in their text content
    if not id_scan:
        for script in script_tags:
            if script.string and "episodes.js?filever=" in script.string:
                match = re.search(r"filever=(\d+)", script.string)
                if match:
                    id_scan = match.group(1)
                    break

    # Method 3: Check for inline scripts that might define the scan ID
    if not id_scan:
        for script in script_tags:
            if script.string:
                # Look for patterns like scanID=123 or idScan=123
                match = re.search(
                    r'(?:scanID|idScan|id_scan|filever)\s*=\s*[\'"]?(\d+)[\'"]?',
                    script.string,
                )
                if match:
                    id_scan = match.group(1)
                    break

    # Method 4: Look for script tags with src attribute containing a version number
    if not id_scan:
        for script in script_tags:
            src = script.get("src")
            if src and re.search(r"\.js\?v=(\d+)", src):
                match = re.search(r"\.js\?v=(\d+)", src)
                if match:
                    id_scan = match.group(1)
                    break

    # Method 5: Look for any HTML element with data-id attribute
    if not id_scan:
        elements_with_data_id = soup.find_all(attrs={"data-id": re.compile(r"\d+")})
        if elements_with_data_id:
            id_scan = elements_with_data_id[0].get("data-id")

    # If all else fails, extract the raw HTML and search for common patterns
    if not id_scan:
        patterns = [
            r"episodes\.js\?filever=(\d+)",
            r"episodes\.js\?v=(\d+)",
            r'scan_id\s*=\s*[\'"]?(\d+)[\'"]?',
            r'id_scan\s*=\s*[\'"]?(\d+)[\'"]?',
            r'scanID\s*=\s*[\'"]?(\d+)[\'"]?',
            r'data-id=[\'"](\d+)[\'"]',
            r"scan/(\d+)/",
        ]

        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                id_scan = match.group(1)
                break

    # Si aucun ID n'a été trouvé, retourne une erreur
    if not id_scan:
        html_sample = (
            html_content[:500] + "..." if len(html_content) > 500 else html_content
        )
        return {
            "error": "ID de scan non trouvé",
            "fullUrl": fullurl,
            "html_sample": html_sample,
        }

    # Étape 2: Maintenant que nous avons l'ID, récupérer les informations du script episodes.js
    episodes_url = f"{urlbase}{name}/{url}/episodes.js?filever={id_scan}"

    # Faire la requête pour récupérer le script episodes.js
    episodes_response = requests.get(episodes_url, headers=headers)

    if episodes_response.status_code != 200:
        return {
            "error": f"Failed to access episodes.js, status code: {episodes_response.status_code}",
            "fullUrl": episodes_url,
        }

    # Le contenu du script episodes.js est généralement du JavaScript, pas du HTML
    # On retourne directement le contenu sous forme de texte, ou on peut essayer de l'analyser si c'est du JSON
    try:
        # Essayer de parser comme du JSON si possible
        if episodes_response.text.strip().startswith(
            "{"
        ) or episodes_response.text.strip().startswith("["):
            import json

            episodes_data = json.loads(episodes_response.text)
            return {
                "success": True,
                "idScan": id_scan,
                "pageUrl": fullurl,
                "scriptUrl": episodes_url,
                "episodes": episodes_data,
            }
        else:
            # Sinon retourner le texte brut
            return {
                "success": True,
                "idScan": id_scan,
                "pageUrl": fullurl,
                "scriptUrl": episodes_url,
                "rawContent": episodes_response.text,
            }
    except Exception as e:
        # En cas d'erreur, retourner le texte brut
        return {
            "success": True,
            "idScan": id_scan,
            "pageUrl": fullurl,
            "scriptUrl": episodes_url,
            "rawContent": episodes_response.text,
            "parseError": str(e),
        }
