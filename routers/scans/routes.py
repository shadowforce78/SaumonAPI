from typing import Annotated
from urllib.parse import quote, unquote
import re

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
def list_oeuvres():
    oeuvres = oeuvres_collection.find().sort("title", pymongo.ASCENDING)
    return [serialize_doc(oeuvre) for oeuvre in oeuvres]


@router.get("/oeuvres/{name}")
def get_oeuvre(name: str):
    oeuvre = oeuvres_collection.find_one(
        {"title": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
    )
    if oeuvre:
        return serialize_doc(oeuvre)
    return {"error": "Oeuvre not found"}


@router.get("/scans/{name}")
def get_scan(name: str):
    scan = scans_collection.find_one(
        {
            "title": {"$regex": f"^{re.escape(name)}$", "$options": "i"},
        }
    )
    if scan:
        return serialize_doc(scan)
    return {"error": "Scan not found"}
