from typing import Annotated

from fastapi import Depends, FastAPI, APIRouter
from fastapi.security import OAuth2PasswordBearer
import pymongo
import dotenv
import os

dotenv.load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
client = pymongo.MongoClient(MONGO_URL)

router = APIRouter(tags=["Scans"])


def untrucate(text: str) -> str:
    #  - => space
    #  _ => '
    text = text.replace(" - ", " ").replace("_", "'")
    return text


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
    untrucated_name = untrucate(manga_name)
    manga = manga_collection.find_one({"title": untrucated_name}, {"_id": 0})
    if not manga:
        return {"error": "Manga not found"}
    return {"manga": manga}


@router.get("/scans/manga/chapter/count")
def get_chapter_count(manga_name: str):
    untrucated_name = untrucate(manga_name)
    data = manga_collection.find_one({"title": untrucated_name}, {"_id": 0})
    if not data:
        return {"error": "Manga not found"}
    count = []
    # for each scan type in the manga data, return the chapters count with name : number
    for scan in data.get("scan_chapters", []):
        count.append(
            {"name": scan.get("name"), "chapters_count": scan.get("chapters_count", 0)}
        )
    return {"chapters_count": count}


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
            "manga_title": untrucate(manga_name),
            "scan_name": untrucate(scans_type),
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

    if untrucate(scans_type) == "Scans":
        pages = [
            f"https://anime-sama.fr/s2/scans/{untrucate(manga_name)}/{chapter}/{i}.jpg"
            for i in range(1, page_count["page_count"])
        ]
    else:
        pages = [
            f"https://anime-sama.fr/s2/scans/{untrucate(manga_name)}%20%E2%80%93%20{untrucate(scans_type)}/{chapter}/{i}.jpg"
            for i in range(1, page_count["page_count"])
        ]
    return {"pages": pages}
