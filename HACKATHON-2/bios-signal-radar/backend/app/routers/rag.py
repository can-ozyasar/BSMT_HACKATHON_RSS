from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
import json
from pathlib import Path

from app.services.rag.engine import rag_engine


router = APIRouter()

_QUESTIONS_FILE = Path("data/rag_questions.json")


class RagAskRequest(BaseModel):
    question: str = Field(min_length=3)
    mode: str = Field(default="genel", description="genel|ozet|arastirma|diyagram")


@router.post("/ask")
async def ask_rag(body: RagAskRequest):
    return await rag_engine.ask(body.question, mode=body.mode)


@router.get("/suggested-questions")
async def get_suggested_questions():
    """Sistemin otomatik ürettiği önerilen sorular."""
    if _QUESTIONS_FILE.exists():
        try:
            data = json.loads(_QUESTIONS_FILE.read_text(encoding="utf-8"))
            return {"questions": data.get("questions", []), "total": len(data.get("questions", []))}
        except Exception:
            pass
    return {"questions": [], "total": 0}


def save_auto_question(question: str):
    """Yeni bir otomatik soru ekler (yineleme yoksa)."""
    try:
        questions = []
        if _QUESTIONS_FILE.exists():
            data = json.loads(_QUESTIONS_FILE.read_text(encoding="utf-8"))
            questions = data.get("questions", [])
        if question not in questions:
            questions.insert(0, question)
        # En fazla 20 soru tut
        questions = questions[:20]
        _QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _QUESTIONS_FILE.write_text(json.dumps({"questions": questions}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

