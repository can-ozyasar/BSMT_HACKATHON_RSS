"""Router: RSS kaynak yönetimi."""
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.storage.rss_store import rss_store
from app.services.collector import validate_rss_url

logger = logging.getLogger("router.rss")
router = APIRouter()


class RssCreate(BaseModel):
    url: str
    name: Optional[str] = None
    tags: list[str] = []


class RssUpdate(BaseModel):
    name: Optional[str] = None
    tags: Optional[list[str]] = None
    starred: Optional[bool] = None


@router.get("")
async def list_rss():
    sources = rss_store.list_all()
    return {"sources": sources, "total": len(sources)}


@router.post("", status_code=201)
async def add_rss(body: RssCreate):
    url = body.url.strip()

    # Duplikasyon kontrolü
    if rss_store.exists_url(url):
        raise HTTPException(
            status_code=409,
            detail={"error": "rss_duplicate", "message": "Bu RSS kaynağı zaten eklenmiş."}
        )

    # RSS validasyonu
    valid, error = await validate_rss_url(url)
    if not valid:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_rss", "message": error or "Bu URL'den RSS okunamadı."}
        )

    source = {
        "id":            f"rss_{uuid.uuid4().hex[:8]}",
        "url":           url,
        "name":          body.name or url.split("/")[2] if "/" in url else url,
        "tags":          body.tags,
        "status":        "active",
        "last_fetched_at": None,
        "error_message": None,
        "added_at":      datetime.now(timezone.utc).isoformat(),
        "article_count": 0,
        "starred": False,
    }

    result = await rss_store.add(source)
    logger.info(f"RSS added: {url}")
    return result


@router.delete("/{source_id}")
async def delete_rss(source_id: str):
    deleted = await rss_store.remove(source_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"error": "rss_not_found", "message": "RSS kaynağı bulunamadı."}
        )
    return {"deleted": source_id, "message": "RSS kaynağı silindi."}


@router.patch("/{source_id}")
async def update_rss(source_id: str, body: RssUpdate):
    data = {k: v for k, v in body.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail={"error": "no_data", "message": "Güncellenecek alan yok."})

    updated = await rss_store.update(source_id, data)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail={"error": "rss_not_found", "message": "RSS kaynağı bulunamadı."}
        )
    return updated
