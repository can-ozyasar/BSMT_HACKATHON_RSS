import os
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# dotenv yükle
from dotenv import load_dotenv
load_dotenv(override=True)

# Loglama
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("main")

# Data dizini oluştur
Path("data/articles").mkdir(parents=True, exist_ok=True)
Path("data/seed").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 BIOS Signal Radar API starting...")
    logger.info(f"   Demo mode:    {os.getenv('DEMO_MODE', 'false')}")
    logger.info(f"   LLM backend:  Ollama @ {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    logger.info(f"   LLM model:    {os.getenv('OLLAMA_MODEL', 'llama3')}")

    # Best-effort: ensure existing article summaries are Turkish (md requirements).
    try:
        from app.storage.articles_store import articles_store
        from app.services.ai_processor import _ensure_summary_tr

        updated = 0
        for a in articles_store.list_all():
            if a.get("analysis_status") != "processed":
                continue
            s = a.get("summary_tr")
            if not s:
                continue
            new_s = await _ensure_summary_tr(s)
            if new_s and new_s != s:
                a["summary_tr"] = new_s
                await articles_store.save(a)
                updated += 1
        if updated:
            logger.info(f"Translated {updated} stored summaries to Turkish.")
    except Exception as e:
        logger.warning(f"summary_tr enforcement skipped: {e}")

    yield
    logger.info("BIOS Signal Radar API stopped.")


app = FastAPI(
    title="BIOS Signal Radar API",
    description="Avrupa endüstriyel haberlerini AI ile analiz eden sistem.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
from app.routers.rss import router as rss_router
from app.routers.articles import router as articles_router
from app.routers.refresh import router as refresh_router
from app.routers.stats import router_anomalies, router_stats, router_health
from app.routers.graph import router as graph_router
from app.routers.rag import router as rag_router

app.include_router(rss_router,       prefix="/api/v1/rss",       tags=["RSS"])
app.include_router(articles_router,  prefix="/api/v1/articles",  tags=["Articles"])
app.include_router(refresh_router,   prefix="/api/v1/refresh",   tags=["Refresh"])
app.include_router(router_anomalies, prefix="/api/v1/anomalies", tags=["Anomalies"])
app.include_router(router_stats,     prefix="/api/v1/stats",     tags=["Stats"])
app.include_router(router_health,    prefix="/api/v1/health",    tags=["Health"])
app.include_router(graph_router,     prefix="/api/v1/graph",     tags=["Graph"])
app.include_router(rag_router,       prefix="/api/v1/rag",       tags=["RAG"])


# ─── Global Hata Handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "Beklenmeyen bir hata oluştu."}
    )


# ─── Demo Seed Endpoint ───────────────────────────────────────────────────────
@app.post("/api/v1/demo/seed", tags=["Demo"])
async def seed_demo():
    """Demo verilerini yükle."""
    import json
    from app.storage.articles_store import articles_store
    from app.storage.rss_store import rss_store

    seed_dir = Path("data/seed")
    seeded = {"articles": 0, "sources": 0}

    # Seed haberler
    seed_articles = seed_dir / "seed_articles.json"
    if seed_articles.exists():
        arts = json.loads(seed_articles.read_text(encoding="utf-8"))
        for a in arts:
            await articles_store.save(a)
        seeded["articles"] = len(arts)

    # Seed RSS kaynakları
    seed_rss = seed_dir / "seed_rss_sources.json"
    if seed_rss.exists():
        sources = json.loads(seed_rss.read_text(encoding="utf-8"))
        for s in sources:
            if not rss_store.exists_url(s["url"]):
                await rss_store.add(s)
        seeded["sources"] = len(sources)

    return {"seeded": seeded, "message": f"Demo verisi yüklendi."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
