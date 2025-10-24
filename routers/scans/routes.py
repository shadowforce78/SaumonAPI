from typing import Annotated
from urllib.parse import quote, unquote
import re

from bson import ObjectId
from fastapi import Depends, FastAPI, APIRouter
from fastapi.security import OAuth2PasswordBearer
import pymongo
import dotenv
import os

dotenv.load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
client = pymongo.MongoClient(MONGO_URL)

router = APIRouter(tags=["Scans"])


def encode_name(text: str) -> str:
    """
    URL encode the text similar to JavaScript's encodeURIComponent
    """
    return quote(text.encode("utf-8"))


def decode_name(text: str) -> str:
    """
    URL decode the text similar to JavaScript's decodeURIComponent
    """
    return unquote(text)


def serialize_doc(doc):
    """
    Convert MongoDB document to JSON-serializable dict by converting ObjectId to string
    """
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        return {
            key: (
                str(value)
                if key == "_id"
                else serialize_doc(value) if isinstance(value, (dict, list)) else value
            )
            for key, value in doc.items()
        }
    return doc


# Define the database
db = client["AnimeSama"]
oeuvres_collection = db["oeuvres"]
utils_collection = db["utils"]
episodes_collection = db["episodes"]
scans_collection = db["scans"]


@router.get("/oeuvres/count")
def count_oeuvres():
    count = oeuvres_collection.count_documents({})
    return {"count": count}


@router.get("/oeuvres")
def list_oeuvres(limit: int = 100, offset: int = 0):
    oeuvres = (
        oeuvres_collection.find()
        .sort("title", pymongo.ASCENDING)
        .skip(offset)
        .limit(limit)
    )
    return [serialize_doc(oeuvre) for oeuvre in oeuvres]


@router.get("/oeuvres/{identifier}")
def get_oeuvre(identifier: str):
    # Try to find by ObjectId first
    if len(identifier) == 24:  # ObjectId length
        try:
            oeuvre = oeuvres_collection.find_one({"_id": ObjectId(identifier)})
            if oeuvre:
                return serialize_doc(oeuvre)
        except:
            pass  # Not a valid ObjectId, continue to search by name

    # Search by exact title match (case-insensitive)
    exact_match = oeuvres_collection.find_one(
        {"title": {"$regex": f"^{re.escape(identifier)}$", "$options": "i"}}
    )

    if exact_match:
        return serialize_doc(exact_match)

    # Search by partial title match (case-insensitive) - return up to 5 results
    partial_matches = list(
        oeuvres_collection.find(
            {"title": {"$regex": f"^{re.escape(identifier)}", "$options": "i"}}
        ).limit(5)
    )

    if partial_matches:
        return [serialize_doc(oeuvre) for oeuvre in partial_matches]

    return {"error": "Oeuvre not found"}


@router.get("/scans/{name}")
def get_scan(name: str):
    scan = scans_collection.find_one(
        {"title": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
    )
    if scan:
        return serialize_doc(scan)
    return {"error": "Scan not found"}


@router.get("/episodes/{name}")
def get_episode(name: str):
    episode = episodes_collection.find_one(
        {"title": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
    )
    if episode:
        return serialize_doc(episode)
    return {"error": "Episode not found"}



@router.get("/utils/genres")
def get_genres():
    utils = utils_collection.find_one()
    if utils:
        return utils.get("genres", [])
    return []


@router.get("/utils/languages")
def get_languages():
    utils = utils_collection.find_one()
    if utils:
        return utils.get("languages", [])
    return []


@router.get("/utils/types")
def get_types():
    utils = utils_collection.find_one()
    if utils:
        return utils.get("types", [])
    return []
