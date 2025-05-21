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

mangaCollec = client["mangas"]
chapterCollec = client["chapters"]

@router.get("/scans/mangacount")
def get_scan_count():
    """
    Get the count of scans in the database.
    """
    count = mangaCollec.count_documents({})
    return {"count": count}

@router.get("/scans/chaptercount")
def get_chapter_count():
    count = chapterCollec.count_documents({})
    return {"count": count}