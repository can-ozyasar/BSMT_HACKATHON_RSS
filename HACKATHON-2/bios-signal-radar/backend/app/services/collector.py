"""RSS Collector — Paralel RSS feed çekimi."""
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import feedparser
import httpx

logger = logging.getLogger("collector")


def _entry_to_dict(entry: dict, source_url: str, source_id: str, source_name: str) -> dict:
    """feedparser entry → ham article dict."""
    title   = getattr(entry, "title",   "") or ""
    link    = getattr(entry, "link",    "") or ""
    summary = getattr(entry, "summary", "") or ""
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "") or ""

    # Yayın tarihi
    published_at = None
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            published_at = dt.isoformat()
        except Exception:
            pass

    # Raw hash
    raw_hash = hashlib.sha256(f"{link}|{title}".encode()).hexdigest()[:16]

    return {
        "title":        title.strip(),
        "original_url": link.strip(),
        "content":      content or summary,
        "source_id":    source_id,
        "source_name":  source_name,
        "source_url":   source_url,
        "published_at": published_at,
        "raw_hash":     raw_hash,
    }


async def fetch_feed(
    source_url: str,
    source_id: str,
    source_name: str,
    max_entries: int = 20,
) -> tuple[list[dict], Optional[str]]:
    """
    Tek RSS kaynağından haberleri çek.
    Returns: (articles_list, error_message_or_None)
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(source_url, headers={"User-Agent": "BIOS-Signal-Radar/1.0"})
        if resp.status_code >= 400:
            msg = f"Bu URL erişilemez (HTTP {resp.status_code})"
            logger.warning(f"fetch_feed: {source_url} → {msg}")
            return [], msg

        feed = feedparser.parse(resp.content)

        if feed.bozo and not feed.entries:
            msg = f"Geçersiz RSS feed: {getattr(feed, 'bozo_exception', 'parse error')}"
            logger.warning(f"fetch_feed: {source_url} → {msg}")
            return [], msg

        entries = feed.entries[:max_entries]
        articles = [_entry_to_dict(e, source_url, source_id, source_name) for e in entries]
        logger.info(f"fetch_feed: {source_url} -> {len(articles)} haber")
        return articles, None

    except httpx.TimeoutException:
        msg = "URL yanıt vermedi (10 sn timeout)"
        logger.error(f"fetch_feed timeout: {source_url} → {msg}")
        return [], msg
    except Exception as e:
        msg = f"Bağlantı hatası: {e}"
        logger.error(f"fetch_feed error: {source_url} → {msg}")
        return [], msg


async def collect_all(sources: list[dict]) -> tuple[list[dict], dict]:
    """
    Tüm RSS kaynaklarından paralel haber çek.
    Returns: (all_articles, errors_by_source_id)
    """
    tasks = [
        fetch_feed(s["url"], s["id"], s.get("name") or s["url"])
        for s in sources
    ]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    all_articles = []
    errors = {}
    for source, (articles, error) in zip(sources, results):
        if error:
            errors[source["id"]] = error
        else:
            all_articles.extend(articles)

    return all_articles, errors


async def validate_rss_url(url: str) -> tuple[bool, Optional[str]]:
    """RSS URL'sinin geçerli olup olmadığını kontrol et."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "BIOS-Signal-Radar/1.0"})
        if resp.status_code >= 400:
            return False, f"Bu URL erişilemez (HTTP {resp.status_code})"

        # Quick HTML check (common invalid case)
        content_type = (resp.headers.get("content-type") or "").lower()
        if "text/html" in content_type and b"<rss" not in resp.content[:2000].lower():
            return False, "Bu URL RSS değil"

        feed = feedparser.parse(resp.content)
        if feed.bozo and not feed.entries:
            exc = getattr(feed, "bozo_exception", None)
            return False, f"RSS okunamadı: {exc}"
        if not feed.entries:
            return False, "Bu URL RSS değil veya içerik boş"
        return True, None
    except httpx.TimeoutException:
        return False, "URL yanıt vermedi (10 sn timeout)"
    except Exception as e:
        return False, f"Bağlantı hatası: {e}"
