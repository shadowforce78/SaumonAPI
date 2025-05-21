from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup, Comment
import re
import pymongo
import dotenv
import os

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
def search_manga(title: str):
    results = manga_collection.find({"title": {"$regex": title, "$options": "i"}})
    return [manga for manga in results]


@router.get("/scans/manga/{title}")
def get_manga(title: str):
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
    
    return manga


@router.get("/scans/chapter/count")
def get_chapter_count():
    count = chapter_collection.count_documents({})
    return {"count": count}
