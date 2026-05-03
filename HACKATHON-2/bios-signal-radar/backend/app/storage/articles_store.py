"""Haberler storage — data/articles/*.json"""
import json
import asyncio
from pathlib import Path
from typing import Optional

DATA_DIR = Path("data")
ARTICLES_DIR = DATA_DIR / "articles"


class ArticlesStore:
    def __init__(self):
        self._lock = asyncio.Lock()
        ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    async def save(self, article: dict):
        async with self._lock:
            path = ARTICLES_DIR / f"{article['id']}.json"
            path.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    def load(self, article_id: str) -> Optional[dict]:
        path = ARTICLES_DIR / f"{article_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_all(self) -> list[dict]:
        articles = []
        for path in ARTICLES_DIR.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                articles.append(data)
            except Exception:
                continue
        # Tarihe göre sırala (yeniden eskiye)
        articles.sort(
            key=lambda a: a.get("published_at") or a.get("fetched_at") or "",
            reverse=True
        )
        return articles

    def filter(
        self,
        min_score: int = 0,
        max_score: int = 100,
        event_type: Optional[str] = None,
        source_id: Optional[str] = None,
        search: Optional[str] = None,
        company: Optional[str] = None,
        sector: Optional[str] = None,
        color: Optional[str] = None,
        sort_by: str = "score",
        sort_order: str = "desc",
        include_failed: bool = True,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[dict]:
        articles = self.list_all()

        # İşlenmiş + (opsiyonel) failed
        if include_failed:
            articles = [a for a in articles if a.get("analysis_status") in ("processed", "failed")]
        else:
            articles = [a for a in articles if a.get("analysis_status") == "processed"]

        # Tarih filtresi (published_at yoksa fetched_at kullan)
        if date_from:
            articles = [
                a for a in articles
                if (a.get("published_at") or a.get("fetched_at") or "") >= date_from
            ]
        if date_to:
            articles = [
                a for a in articles
                if (a.get("published_at") or a.get("fetched_at") or "") <= date_to
            ]

        # Skor filtresi (failed için skor 0 varsay)
        articles = [
            a for a in articles
            if min_score <= (a.get("bios_fit", {}) or {}).get("score_final", 0) <= max_score
        ]

        # Olay tipi filtresi
        if event_type:
            articles = [a for a in articles if a.get("event_type") == event_type]

        # Kaynak filtresi
        if source_id:
            articles = [a for a in articles if a.get("source_id") == source_id]

        # Renk filtresi
        if color:
            articles = [
                a for a in articles
                if (a.get("bios_fit", {}) or {}).get("color") == color
            ]

        # Arama
        if search:
            q = search.lower()
            articles = [
                a for a in articles
                if q in (a.get("title") or "").lower()
                or q in (a.get("summary_tr") or "").lower()
                or q in (a.get("company") or "").lower()
            ]

        # Şirket filtresi (case-insensitive contains)
        if company:
            cq = company.lower()
            articles = [a for a in articles if cq in (a.get("company") or "").lower()]

        # Sektör filtresi (case-insensitive contains)
        if sector:
            sq = sector.lower()
            articles = [a for a in articles if sq in (a.get("sector") or "").lower()]

        # Sıralama
        reverse = sort_order == "desc"
        if sort_by == "score":
            articles.sort(
                key=lambda a: (a.get("bios_fit", {}) or {}).get("score_final", 0),
                reverse=reverse
            )
        elif sort_by in ("date", "published_at"):
            articles.sort(
                key=lambda a: a.get("published_at") or a.get("fetched_at") or "",
                reverse=reverse
            )
        elif sort_by == "company":
            articles.sort(
                key=lambda a: (a.get("company") or "").lower(),
                reverse=reverse
            )

        return articles

    def exists(self, article_id: str) -> bool:
        return (ARTICLES_DIR / f"{article_id}.json").exists()

    async def delete(self, article_id: str) -> bool:
        path = ARTICLES_DIR / f"{article_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def count(self) -> int:
        return len(list(ARTICLES_DIR.glob("*.json")))


articles_store = ArticlesStore()
