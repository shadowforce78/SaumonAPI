from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup, Comment
import re
import pymongo
from bson import ObjectId
import json
import dotenv
import os
from typing import Dict, List, Any

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
def search_manga(title: str) -> List[Dict[str, Any]]:
    regex_query = {"title": {"$regex": title, "$options": "i"}}
    results = list(manga_collection.find(regex_query, {"title": 1, "genres": 1, "type": 1}))
    # Serialize each document to handle ObjectId
    return [serialize_doc(manga) for manga in results]


@router.get("/scans/manga/{title}")
def get_manga(title: str) -> Dict[str, Any]:
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
    
    # Serialize the document to handle ObjectId
    return serialize_doc(manga)


@router.get("/scans/chapter/count")
def get_chapter_count():
    count = chapter_collection.count_documents({})
    return {"count": count}
