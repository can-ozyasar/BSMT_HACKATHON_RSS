"""Graph Router — Knowledge graph data endpoint."""
from fastapi import APIRouter
from app.services.graph_engine import graph_engine
from app.storage.articles_store import articles_store

router = APIRouter()


@router.get("")
async def get_graph():
    """
    Returns the knowledge graph: nodes enriched with article metadata
    and edges representing company/location relationships.
    Edges are rebuilt on-the-fly from the current articles store.
    """
    all_articles = articles_store.list_all()
    processed = [a for a in all_articles if a.get("analysis_status") == "processed"]

    # Always rebuild edges from current articles
    edges = graph_engine.build_graph_edges(processed)

    # Build enriched nodes from all processed articles
    enriched_nodes = []
    for article in processed:
        bios = article.get("bios_fit") or {}
        enriched_nodes.append({
            "id": article.get("id"),
            "label": article.get("company") or (article.get("title", "")[:40]),
            "title": article.get("title", ""),
            "company": article.get("company"),
            "location": article.get("to_location") or article.get("from_location"),
            "event_type": article.get("event_type", "other"),
            "signal_type": article.get("signal_type", "neutral"),
            "score": bios.get("score_final", 0),
            "sector": article.get("sector"),
            "summary_tr": article.get("summary_tr", ""),
            "published_at": article.get("published_at"),
        })

    return {
        "nodes": enriched_nodes,
        "edges": edges,
        "total_nodes": len(enriched_nodes),
        "total_edges": len(edges),
    }
