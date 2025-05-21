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


@router.get("/scans/count")
def get_scan_count():
    """
    Get the count of scans in the database.
    """
    db = client["SushiScan"]
    collection = db["mangas"]
    count = collection.count_documents({})
    return {"count": count}