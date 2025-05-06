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
        if len(anime_disponibles) > 0 :
            anime_disponibles.pop(0)

        # Extraire les types de scans à partir des appels à panneauScan()
        scans_disponibles = []
        scan_pattern = r'panneauScan\("([^"]+)",\s*"([^"]+)"\);'
        scan_matches = re.findall(scan_pattern, html_content)
        for match in scan_matches:
            nom, url = match
            scans_disponibles.append({"nom": nom, "url": url})
            
        if len(scans_disponibles) > 0 :
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