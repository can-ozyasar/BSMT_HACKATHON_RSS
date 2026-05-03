"""Router: Refresh pipeline."""
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.refresh_pipeline import run_refresh

logger = logging.getLogger("router.refresh")
router = APIRouter()

# Basit job tracker
_jobs: dict[str, dict] = {}


class RefreshRequest(BaseModel):
    source_ids: Optional[list[str]] = None
    force: bool = False


@router.post("", status_code=202)
async def start_refresh(body: RefreshRequest, background_tasks: BackgroundTasks):
    import uuid
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    _jobs[job_id] = {"status": "running", "result": None}

    async def do_refresh():
        try:
            result = await run_refresh(body.source_ids)
            _jobs[job_id] = {"status": "completed", "result": result}
        except Exception as e:
            logger.error(f"Refresh job {job_id} failed: {e}")
            _jobs[job_id] = {"status": "failed", "result": {"error": str(e)}}

    background_tasks.add_task(do_refresh)
    return {"job_id": job_id, "status": "running"}


@router.get("/{job_id}/status")
async def get_refresh_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return {"job_id": job_id, "status": "not_found"}
    return {"job_id": job_id, **job}


@router.post("/sync")
async def sync_refresh(body: RefreshRequest):
    """Senkron refresh (test için)."""
    result = await run_refresh(body.source_ids)
    return result
