from fastapi import APIRouter, HTTPException, BackgroundTasks
import requests
from bs4 import BeautifulSoup, Comment
import re
import pymongo
from bson import ObjectId
import json
import dotenv
import os
from typing import Dict, List, Any
from random import sample

# Custom JSON encoder for handling MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)

# Helper function to convert MongoDB documents to serializable dictionaries
def serialize_doc(doc: Dict) -> Dict:
    if doc is None:
        return None
    
    # Convert MongoDB document to Python dict and handle ObjectId
    doc_dict = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc_dict[key] = str(value)
        elif isinstance(value, list) and all(isinstance(x, ObjectId) for x in value):
            doc_dict[key] = [str(x) for x in value]
        else:
            doc_dict[key] = value
    return doc_dict

# Function to update manga popularity when it is viewed/searched
async def update_manga_popularity(title: str, background_tasks: BackgroundTasks):
    """Increment the popularity counter for a manga by 1"""
    background_tasks.add_task(
        manga_collection.update_one,
        {"title": {"$regex": f"^{re.escape(title)}$", "$options": "i"}},
        {"$inc": {"popularity": 1}},
        upsert=False
    )

# Initialize manga popularity based on chapter count (run once)
async def initialize_manga_popularity(force_update: bool = False):
    """Initialize popularity field for all mangas based on chapter count"""
    # Check if popularity has been initialized - only run once
    if not force_update:
        has_popularity = manga_collection.find_one({"popularity": {"$exists": True}})
        if has_popularity:
            return False
    
    # Get all mangas and update popularity based on chapter count
    cursor = manga_collection.find({})
    
    for manga in cursor:
        chapter_count = manga.get("chapter_count", 0)
        # Set initial popularity based on chapter count (with some base value)
        initial_popularity = max(10, chapter_count * 2)  # At least 10, or 2 times chapters
        
        manga_collection.update_one(
            {"_id": manga["_id"]},
            {"$set": {"popularity": initial_popularity}}
        )
    
    return True

dotenv.load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
client = pymongo.MongoClient(MONGO_URL)

router = APIRouter(tags=["Scans"])

# Define the database
db = client["SushiScan"]
# Define collections within the database
manga_collection = db["mangas"]
chapter_collection = db["chapters"]


@router.get("/scans/manga/count")
def get_scan_count():
    """
    Get the count of scans in the database.
    """
    count = manga_collection.count_documents({})
    return {"count": count}


@router.get("/scans/manga/search")
async def search_manga(title: str, background_tasks: BackgroundTasks) -> List[Dict[str, Any]]:
    regex_query = {"title": {"$regex": title, "$options": "i"}}
    results = list(manga_collection.find(regex_query, {"title": 1, "genres": 1, "type": 1}))
    
    # Increment popularity for each manga found (in background)
    for manga in results:
        if "title" in manga:
            await update_manga_popularity(manga["title"], background_tasks)
    
    # Serialize each document to handle ObjectId
    return [serialize_doc(manga) for manga in results]


@router.get("/scans/manga/{title}")
async def get_manga(title: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    # Normalize the title to handle different formats
    # First, try an exact case-insensitive match
    manga = manga_collection.find_one({"title": {"$regex": f"^{re.escape(title)}$", "$options": "i"}})
    
    if not manga:
        # If no exact match, try a more flexible match by replacing dashes with spaces and vice versa
        normalized_title = title.replace("-", " ")
        manga = manga_collection.find_one({
            "$or": [
                {"title": {"$regex": f"^{re.escape(normalized_title)}$", "$options": "i"}},
                {"title": {"$regex": f"^{re.escape(title.replace(' ', '-'))}$", "$options": "i"}}
            ]
        })
    
    if not manga:
        # If still no match, try a partial match
        manga = manga_collection.find_one({"title": {"$regex": re.escape(title), "$options": "i"}})
    
    if not manga:
        raise HTTPException(status_code=404, detail=f"Manga not found: {title}")
    
    # Increment popularity counter (in background)
    await update_manga_popularity(manga["title"], background_tasks)
    
    # Serialize the document to handle ObjectId
    return serialize_doc(manga)


@router.get("/scans/homepage")
async def get_homepage_mangas(background_tasks: BackgroundTasks) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get a curated list of popular and recommended manga for the homepage.
    
    Returns different categories:
    - Trending: Mangas with highest popularity score
    - Popular: Mangas with popular genres like shonen, action, etc.
    - Recommended: A random selection of mangas
    """
    # Initialize popularity for mangas if not already done
    background_tasks.add_task(initialize_manga_popularity)
    
    # Projection to limit the fields returned
    projection = {
        "title": 1, 
        "image": 1, 
        "genres": 1, 
        "type": 1, 
        "status": 1, 
        "chapter_count": 1, 
        "popularity": 1,
        "last_updated": 1
    }
    
    # Get trending manga (those with highest popularity, limited to 10)
    trending_cursor = manga_collection.find(
        {}, 
        projection
    ).sort("popularity", pymongo.DESCENDING).limit(10)
    trending = [serialize_doc(manga) for manga in trending_cursor]
    
    # If not enough trending mangas found, fallback to chapter count
    if len(trending) < 5:
        trending_cursor = manga_collection.find(
            {}, 
            projection
        ).sort("chapter_count", pymongo.DESCENDING).limit(10)
        trending = [serialize_doc(manga) for manga in trending_cursor]
    
    # Get popular genres manga (e.g., shonen, action, adventure)
    popular_genres = ["Shonen", "Action", "Adventure", "Fantasy"]
    popular_cursor = manga_collection.find(
        {"genres": {"$in": popular_genres}}, 
        projection
    ).sort("popularity", pymongo.DESCENDING).limit(10)
    popular = [serialize_doc(manga) for manga in popular_cursor]
    
    # Get some random recommendations
    # First get the total count
    total_manga = manga_collection.count_documents({})
    # Then get a sample of mangas (up to 10)
    limit = min(10, total_manga)
    if limit > 0:
        # Get a random sample using aggregation
        random_cursor = manga_collection.aggregate([
            {"$sample": {"size": limit}},
            {"$project": projection}
        ])
        recommended = [serialize_doc(manga) for manga in random_cursor]
    else:
        recommended = []
    
    # Create the response
    return {
        "trending": trending,
        "popular": popular,
        "recommended": recommended
    }


@router.get("/scans/chapter/count")
def get_chapter_count():
    count = chapter_collection.count_documents({})
    return {"count": count}

@router.get("/scans/chapter")
async def get_chapter(title: str, scan_name: str, chapter_number: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Récupère un chapitre spécifique d'un manga par son titre, le nom du scan et le numéro de chapitre.
    
    Parameters:
    - title: Le titre du manga
    - scan_name: Le nom du scan (ex: "Scan VF")
    - chapter_number: Le numéro du chapitre (peut être une chaîne comme "1" ou "1.5")
    
    Returns:
    - Les informations du chapitre avec les URLs des images
    """
    # Recherche du chapitre dans la collection
    # Utilisation de re.escape pour les paramètres de la regex pour éviter les erreurs avec les caractères spéciaux
    query = {
        "manga_title": {"$regex": f"^{re.escape(title)}$", "$options": "i"},
        "scan_name": {"$regex": f"^{re.escape(scan_name)}$", "$options": "i"},
        "number": chapter_number 
    }
    chapter_doc = chapter_collection.find_one(query)
    
    if not chapter_doc:
        # Si aucune correspondance exacte n'est trouvée, essayer avec des titres normalisés
        # (remplacer les tirets par des espaces et vice-versa pour le titre du manga)
        normalized_title_space = title.replace("-", " ")
        normalized_title_dash = title.replace(" ", "-")
        
        or_conditions = []
        if normalized_title_space != title:
            or_conditions.append({
                "manga_title": {"$regex": f"^{re.escape(normalized_title_space)}$", "$options": "i"},
                "scan_name": {"$regex": f"^{re.escape(scan_name)}$", "$options": "i"},
                "number": chapter_number
            })
        if normalized_title_dash != title:
            or_conditions.append({
                "manga_title": {"$regex": f"^{re.escape(normalized_title_dash)}$", "$options": "i"},
                "scan_name": {"$regex": f"^{re.escape(scan_name)}$", "$options": "i"},
                "number": chapter_number
            })
        
        if or_conditions:
            chapter_doc = chapter_collection.find_one({"$or": or_conditions})

    if not chapter_doc:
        raise HTTPException(
            status_code=404,
            detail=f"Chapitre non trouvé: Manga '{title}', Scan '{scan_name}', Chapitre '{chapter_number}'"
        )
    
    # Sérialiser le document pour gérer les ObjectId et autres types non sérialisables
    serialized_chapter = serialize_doc(chapter_doc)

    # Mettre à jour la popularité du manga en arrière-plan
    # Assurez-vous que manga_title existe dans le document avant de l'utiliser
    if "manga_title" in serialized_chapter:
        await update_manga_popularity(serialized_chapter["manga_title"], background_tasks)
    
    return serialized_chapter


@router.post("/scans/init-popularity")
async def init_popularity(force: bool = False) -> Dict[str, Any]:
    """
    Initialize the popularity field for all mangas based on their chapter count.
    Only needed to be run once or when manually triggering a reset.
    
    Parameters:
    - force: If True, will reinitialize popularity even if it already exists.
    """
    result = await initialize_manga_popularity(force_update=force)
    if result:
        return {"status": "success", "message": "Manga popularity initialized successfully"}
    else:
        return {"status": "skipped", "message": "Manga popularity already initialized. Use force=true to reinitialize."}