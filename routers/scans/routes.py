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
    manga = manga_collection.find_one({"title": title})
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    return manga


@router.get("/scans/chapter/count")
def get_chapter_count():
    count = chapter_collection.count_documents({})
    return {"count": count}
