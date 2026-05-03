"""Normalizer — HTML temizle, dil tespit, dedup hash."""
import hashlib
import logging
from typing import Optional

from app.utils.html_clean import clean_html

logger = logging.getLogger("normalizer")

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_OK = True
except ImportError:
    LANGDETECT_OK = False


def detect_language(text: str) -> Optional[str]:
    if not LANGDETECT_OK or not text.strip():
        return None
    try:
        return detect(text[:500])
    except Exception:
        return None


def normalize(raw_article: dict) -> Optional[dict]:
    """
    Ham article'ı normalize et.
    Returns: Temizlenmiş article dict veya None (boş ise)
    """
    title   = clean_html(raw_article.get("title", ""))
    content = clean_html(raw_article.get("content", ""))

    full_text = f"{title}. {content}".strip()
    if len(full_text) < 30:
        logger.debug(f"Skipping too-short article: {title[:50]}")
        return None

    language = detect_language(full_text)
    content_hash = hashlib.sha256(full_text[:500].encode()).hexdigest()[:16]

    return {
        **raw_article,
        "title":          title,
        "content":        content[:2000],   # Max 2K karakter sakla
        "content_preview": content[:300],
        "language":       language,
        "content_hash":   content_hash,
    }
