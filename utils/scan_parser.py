import re

def parse_raw_scan_content(raw_content: str) -> dict:
    """
    Parse le contenu brut des scans et extrait les URLs des images par chapitre.
    
    Args:
        raw_content: Contenu brut au format JavaScript avec des déclarations de variables comme 'var epsX= [...]'
        
    Returns:
        Un dictionnaire avec les chapitres et leurs images
    """
    # Structure pour stocker les résultats
    chapters = {}
    
    # Utiliser une expression régulière pour trouver toutes les définitions de variables de type eps
    pattern = r'var\s+(eps\d+)\s*=\s*\[(.*?)(?=\]\s*;)'
    matches = re.findall(pattern, raw_content, re.DOTALL)
    
    for chapter_name, urls_content in matches:
        # Extraire le numéro du chapitre
        chapter_number = int(chapter_name.replace('eps', ''))
        
        # Traiter les URLs dans ce chapitre
        urls = []
        url_pattern = r"'(https://[^']+)'"
        url_matches = re.findall(url_pattern, urls_content)
        
        for url in url_matches:
            # Extraire l'ID du Google Drive si présent
            drive_id_match = re.search(r'id=([^&]+)', url)
            drive_id = drive_id_match.group(1) if drive_id_match else None
            
            urls.append({
                "url": url,
                "drive_id": drive_id
            })
        
        # Ajouter ce chapitre au dictionnaire résultat
        chapters[chapter_number] = {
            "name": f"Chapitre {chapter_number}",
            "images_count": len(urls),
            "images": urls
        }
    
    # Créer la structure finale
    result = {
        "total_chapters": len(chapters),
        "chapters": sorted(chapters.items(), key=lambda x: x[0])
    }
    
    return result

def get_formatted_scan_content(raw_content: str) -> dict:
    """
    Formate le contenu brut des scans dans un format plus utilisable.
    
    Args:
        raw_content: Contenu brut au format JavaScript
        
    Returns:
        Un dictionnaire structuré contenant les chapitres et les images
    """
    try:
        # Parser le contenu brut
        parsed_data = parse_raw_scan_content(raw_content)
        
        # Restructurer dans un format plus simple pour l'API
        chapters = []
        for chapter_num, chapter_data in parsed_data["chapters"]:
            chapters.append({
                "number": chapter_num,
                "name": chapter_data["name"],
                "images_count": chapter_data["images_count"],
                "images": chapter_data["images"]
            })
        
        return {
            "success": True,
            "message": "Contenu des scans analysé avec succès",
            "total_chapters": parsed_data["total_chapters"],
            "chapters": chapters
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de l'analyse du contenu des scans: {str(e)}",
            "raw_content": raw_content[:100] + "..." # Afficher une partie du contenu brut pour le débogage
        }