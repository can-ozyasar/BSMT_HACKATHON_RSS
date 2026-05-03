"""Router: Haber listesi ve detay."""
import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.storage.articles_store import articles_store
from app.services.graph_engine import graph_engine
from app.services.synapse_ai import compute_synapse_ai

logger = logging.getLogger("router.articles")
router = APIRouter()


@router.get("")
async def list_articles(
    min_score: int = Query(0, ge=0, le=100),
    max_score: int = Query(100, ge=0, le=100),
    event_type: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    sort_by: str = Query("score"),
    sort_order: str = Query("desc"),
    include_failed: bool = Query(True),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    # UI sends `published_at` — normalize to store's accepted values.
    if sort_by == "published_at":
        sort_by = "published_at"

    all_articles = articles_store.filter(
        min_score=min_score,
        max_score=max_score,
        event_type=event_type,
        source_id=source_id,
        search=search,
        company=company,
        sector=sector,
        color=color,
        sort_by=sort_by,
        sort_order=sort_order,
        include_failed=include_failed,
        date_from=date_from,
        date_to=date_to,
    )

    total = len(all_articles)
    start = (page - 1) * limit
    end = start + limit
    page_articles = all_articles[start:end]

    # Synapse score can change as the graph evolves; compute on-the-fly for responses
    try:
        processed_all = [a for a in articles_store.list_all() if a.get("analysis_status") == "processed"]
        edges = graph_engine.build_graph_edges(processed_all)
        for a in page_articles:
            aid = a.get("id")
            if not aid:
                continue
            syn, br = graph_engine.calculate_synapse_score(aid, edges, processed_all)
            a["synapse_score"] = syn
            a["synapse_breakdown"] = br
    except Exception as e:
        logger.warning(f"Synapse on-the-fly compute failed: {e}")

    # Özet
    all_scores = [(a.get("bios_fit") or {}).get("score_final", 0) for a in all_articles]
    summary = {
        "total_articles":    total,
        "high_opportunity":  sum(1 for s in all_scores if s >= 80),
        "watchlist":         sum(1 for s in all_scores if 65 <= s < 80),
        "conditional":       sum(1 for s in all_scores if 50 <= s < 65),
        "low_relevance":     sum(1 for s in all_scores if s < 50),
    }

    return {
        "articles": page_articles,
        "pagination": {
            "page": page, "limit": limit, "total": total,
            "total_pages": (total + limit - 1) // limit if total else 1,
            "has_next": end < total,
        },
        "summary": summary,
    }


@router.get("/{article_id}")
async def get_article(article_id: str, include_synapse_ai: bool = Query(False)):
    article = articles_store.load(article_id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail={"error": "article_not_found", "message": "Haber bulunamadı."}
        )
    # Enrich with current synapse score (graph-derived)
    try:
        processed_all = [a for a in articles_store.list_all() if a.get("analysis_status") == "processed"]
        edges = graph_engine.build_graph_edges(processed_all)
        syn, br = graph_engine.calculate_synapse_score(article_id, edges, processed_all)
        article["synapse_score"] = syn
        article["synapse_breakdown"] = br

        if include_synapse_ai and article.get("analysis_status") == "processed":
            cached = article.get("synapse_ai") or {}
            if not cached.get("synapse_ai_score"):
                neighbors = graph_engine.get_neighbors(article_id, processed_all, edges)
                features = graph_engine.build_synapse_features(article_id, edges, processed_all)
                ai = await compute_synapse_ai(article, neighbors, features)
                if ai:
                    article["synapse_ai"] = ai
                    await articles_store.save(article)
    except Exception as e:
        logger.warning(f"Synapse compute failed for {article_id}: {e}")

    return article


@router.delete("/{article_id}")
async def delete_article(article_id: str):
    deleted = await articles_store.delete(article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"error": "not_found"})
    return {"deleted": article_id}
