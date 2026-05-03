"""RSS kaynakları storage — data/rss_sources.json"""
import json
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

DATA_DIR = Path("data")
RSS_FILE = DATA_DIR / "rss_sources.json"


class RssStore:
    def __init__(self):
        self._lock = asyncio.Lock()
        DATA_DIR.mkdir(exist_ok=True)
        if not RSS_FILE.exists():
            RSS_FILE.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            return json.loads(RSS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    async def _save(self, sources: list[dict]):
        async with self._lock:
            RSS_FILE.write_text(
                json.dumps(sources, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    def list_all(self) -> list[dict]:
        return self._load()

    def list_active(self) -> list[dict]:
        return [s for s in self._load() if s.get("status") != "error"]

    def get(self, source_id: str) -> Optional[dict]:
        for s in self._load():
            if s["id"] == source_id:
                return s
        return None

    def exists_url(self, url: str) -> bool:
        return any(s["url"] == url for s in self._load())

    async def add(self, source: dict) -> dict:
        sources = self._load()
        sources.append(source)
        await self._save(sources)
        return source

    async def remove(self, source_id: str) -> bool:
        sources = self._load()
        new = [s for s in sources if s["id"] != source_id]
        if len(new) == len(sources):
            return False
        await self._save(new)
        return True

    async def update_status(self, source_id: str, status: str,
                            error_message: Optional[str] = None,
                            last_fetched_at: Optional[str] = None,
                            article_count: Optional[int] = None):
        sources = self._load()
        for s in sources:
            if s["id"] == source_id:
                s["status"] = status
                if error_message is not None:
                    s["error_message"] = error_message
                if last_fetched_at is not None:
                    s["last_fetched_at"] = last_fetched_at
                if article_count is not None:
                    s["article_count"] = article_count
                break
        await self._save(sources)

    async def update(self, source_id: str, data: dict) -> Optional[dict]:
        sources = self._load()
        for s in sources:
            if s["id"] == source_id:
                s.update(data)
                await self._save(sources)
                return s
        return None


# Global instance
rss_store = RssStore()
