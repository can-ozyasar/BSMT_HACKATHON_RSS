"""Router: Anomaliler ve stats."""
import logging
import os
from fastapi import APIRouter

from app.services.anomaly_engine import anomaly_engine
from app.storage.articles_store import articles_store
from app.storage.rss_store import rss_store

logger = logging.getLogger("router.stats")
router_anomalies = APIRouter()
router_stats = APIRouter()
router_health = APIRouter()


@router_anomalies.get("")
async def list_anomalies():
    window = int(os.getenv("ANOMALY_WINDOW_HOURS", 6))
    baseline = int(os.getenv("ANOMALY_BASELINE_DAYS", 7))
    threshold = float(os.getenv("ANOMALY_SPIKE_THRESHOLD", 4.0))
    anomalies = anomaly_engine.detect(window, baseline, threshold)
    return {"anomalies": anomalies, "total": len(anomalies)}


@router_stats.get("")
async def get_stats():
    all_articles = articles_store.filter()
    scores = [(a.get("bios_fit") or {}).get("score_final", 0) for a in all_articles]
    sources = rss_store.list_all()

    event_types = {}
    sectors = {}
    for a in all_articles:
        et = a.get("event_type", "other")
        event_types[et] = event_types.get(et, 0) + 1
        sec = a.get("sector", "other")
        sectors[sec or "other"] = sectors.get(sec or "other", 0) + 1

    anomalies = anomaly_engine.detect()
    last_refresh = max(
        (s.get("last_fetched_at") or "" for s in sources),
        default=None
    ) or None

    return {
        "articles": {
            "total": len(all_articles),
            "high_opportunity": sum(1 for s in scores if s >= 80),
            "watchlist":        sum(1 for s in scores if 65 <= s < 80),
            "conditional":      sum(1 for s in scores if 50 <= s < 65),
            "low_relevance":    sum(1 for s in scores if s < 50),
            "by_event_type": event_types,
            "by_sector": sectors,
        },
        "sources": {
            "total": len(sources),
            "active": sum(1 for s in sources if s.get("status") == "active"),
            "last_refresh": last_refresh,
        },
        "anomalies": {
            "active_count": len(anomalies),
        },
    }


@router_health.get("")
async def health_check():
    import httpx
    from app.config import get_settings
    settings = get_settings()

    # Check if Ollama is reachable
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_status = "ok" if r.status_code == 200 else f"error:{r.status_code}"
    except Exception as e:
        ollama_status = f"unreachable: {e}"

    return {
        "status": "ok",
        "llm_backend": "ollama",
        "ollama_url": settings.ollama_base_url,
        "ollama_model": settings.ollama_model,
        "ollama_status": ollama_status,
        "demo_mode": settings.demo_mode,
        "version": "1.0.0",
    }
