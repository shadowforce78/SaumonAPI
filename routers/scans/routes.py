from typing import Annotated
from urllib.parse import quote, unquote

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


# Define the database
db = client["SushiScan"]
# Define collections within the database
manga_collection = db["mangas"]
chapter_collection = db["chapters"]
planning_collection = db["planning"]
homepage_collection = db["homepage"]


@router.get("/scans/manga/count")
def get_scan_count():
    """
    Get the count of scans in the database.
    """
    count = manga_collection.count_documents({})
    return {"count": count}


@router.get("/scans/manga")
def search_manga(query: str):
    """
    Search for manga by title.
    """
    results = list(
        manga_collection.find({"title": {"$regex": query, "$options": "i"}}, {"_id": 0})
    )
    return {"results": results}


@router.get("/scans/mangaList")
def get_manga_list(limit: int = 50, skip: int = 0):
    """
    Get the list of all manga in the database.
    """
    mangas = list(manga_collection.find({}, {"_id": 0}).skip(skip).limit(limit))
    return {"mangas": mangas}


@router.get("/scans/manga/info")
def get_manga_info(manga_name: str):
    """
    Get detailed information about a specific manga.
    """
    decoded_name = decode_name(manga_name)
    manga = manga_collection.find_one({"title": decoded_name}, {"_id": 0})
    if not manga:
        return {"error": "Manga not found"}
    return {"manga": manga}


@router.get("/scans/manga/chapter/count")
def get_chapter_count(manga_name: str):
    decoded_name = decode_name(manga_name)
    data = manga_collection.find_one({"title": decoded_name}, {"_id": 0})
    if not data:
        return {"error": "Manga not found"}
    count = []
    # for each scan type in the manga data, return the chapters count with name : number
    for scan in data.get("scan_chapters", []):
        count.append(
            {"name": scan.get("name"), "chapters_count": scan.get("chapters_count", 0)}
        )
    return {"chapters_count": count}


@router.get("/scans/manga/classics")
def get_classic_manga():
    """
    Get a list of classic manga from homepage collection.
    """
    for homepage in homepage_collection.find(
        {}, {"_id": 0, "sections.classiques": 1, "statistics.classiques_count": 1}
    ):
        if "classiques" in homepage["sections"]:
            return {
                "classics": homepage["sections"]["classiques"]["items"],
                "count": homepage["statistics"]["classiques_count"],
            }


@router.get("/scans/manga/recommended")
def get_recommended_manga():
    """
    Get a list of recommended manga from homepage collection.
    """
    for homepage in homepage_collection.find(
        {}, {"_id": 0, "sections.pepites": 1, "statistics.pepites_count": 1}
    ):
        if "pepites" in homepage["sections"]:
            return {
                "recommended": homepage["sections"]["pepites"]["items"],
                "count": homepage["statistics"]["pepites_count"],
            }
    return {"error": "No recommended manga found"}

@router.get("/scans/manga/last")
def get_last_manga():
    """
    Get a list of the last manga added to the database.
    derniers_scans in db
    """
    for homepage in homepage_collection.find(
        {}, {"_id": 0, "sections.derniers_scans": 1, "statistics.derniers_scans_count": 1}
    ):
        if "derniers_scans" in homepage["sections"]:
            return {
                "last_manga": homepage["sections"]["derniers_scans"]["items"],
                "count": homepage["statistics"]["derniers_scans_count"],
            }


@router.get("/scans/chapter/count")
def get_all_chapter_count():
    count = chapter_collection.count_documents({})
    return {"count": count}


@router.get("/scans/chapter/pages/count")
def get_all_chapter_pages_count(manga_name: str, scans_type: str, chapter: str):
    """
    Get the count of pages in a specific chapter.
    """
    data = chapter_collection.find_one(
        {
            "manga_title": decode_name(manga_name),
            "scan_name": decode_name(scans_type),
            "number": chapter,
        },
        {"_id": 0},
    )
    if not data:
        return {"error": "Chapter not found"}
    return {"page_count": data.get("page_count", 0)}


@router.get("/scans/chapter/pages")
def get_all_chapter_pages(manga_name: str, scans_type: str, chapter: str):
    """
    Get all pages of a specific chapter.
    """
    page_count = get_all_chapter_pages_count(manga_name, scans_type, chapter)
    if "error" in page_count:
        return page_count

    if decode_name(scans_type) == "Scans":
        pages = [
            f"https://anime-sama.fr/s2/scans/{decode_name(manga_name)}/{chapter}/{i}.jpg"
            for i in range(1, page_count["page_count"])
        ]
    else:
        pages = [
            f"https://anime-sama.fr/s2/scans/{decode_name(manga_name)}%20{decode_name(scans_type)}/{chapter}/{i}.jpg"
            for i in range(1, page_count["page_count"])
        ]
    return {"pages": pages}


@router.get("/scans/planning")
def get_scans_planning():
    """
    Get the planning of upcoming scans.
    """
    planning = list(
        planning_collection.find({}, {"_id": 0}).sort("updated_at", pymongo.ASCENDING)
    )
    if not planning:
        return {"error": "No planning found"}
    return {"planning": planning}
