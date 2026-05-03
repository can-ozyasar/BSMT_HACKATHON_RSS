"""AI Processor — 2-turlu Llama3 (Ollama) pipeline.

Gemini API'yi tamamen kaldırdık. Artık yerel olarak çalışan Ollama sunucusunu
OpenAI-uyumlu /api/chat endpoint'i üzerinden kullanıyoruz.
"""
import asyncio
import json
import logging
import os
import re
from typing import Optional
from datetime import datetime, timezone

import httpx
from pydantic import BaseModel, Field

from app.utils.json_safe import parse_json_safe
try:
    from langdetect import detect
    _LANGDETECT_OK = True
except Exception:
    _LANGDETECT_OK = False

# ─── Pydantic Şemalar (belgeleme / iç doğrulama için) ─────────────────────────

class Turn1Schema(BaseModel):
    relevant: bool
    confidence: float
    signal_hint: str = Field(default="")

class Turn1BatchItem(BaseModel):
    id: str
    relevant: bool
    confidence: float
    signal_hint: str = Field(default="")

class Turn1BatchSchema(BaseModel):
    results: list[Turn1BatchItem]

class Turn2Schema(BaseModel):
    event_type: str = Field(description="relocation, closure, expansion, tender, or other")
    summary_tr: str
    company: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None
    timeline: Optional[str] = None
    capex_eur: Optional[float] = None
    jobs_impact: Optional[int] = None
    line_type: Optional[str] = None
    equipment_keywords: list[str] = Field(default_factory=list)
    signal_type: str = Field(description="positive, negative, or neutral")
    confidence: float
    reasoning: str
    assumptions: list[str] = Field(default_factory=list)

logger = logging.getLogger("ai_processor")

# ─── Ollama Ayarları ──────────────────────────────────────────────────────────

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")
DEMO_MODE       = os.getenv("DEMO_MODE", "false").lower() == "true"

SEMAPHORE = asyncio.Semaphore(2)   # Llama3 yerel: daha küçük concurrency

# ─── Prompts ─────────────────────────────────────────────────────────────────

PROMPT_TURN1_SYSTEM = """You are an industrial news classifier for BIOS Signal Radar.

Classify whether a news article belongs to one of these RELEVANT signal categories:

1. FACTORY & PRODUCTION MOVEMENT - factory relocation, closure, new plant, capacity change
2. WORKFORCE & RESTRUCTURING - mass layoffs (500+ people), workforce reduction, consolidation
3. STRATEGIC CORPORATE NEWS - major M&A, bankruptcy, outsourcing decisions, supply chain restructuring
4. INVESTMENT & TENDER - major CapEx announcements, industrial equipment tenders, government-backed factory investments
5. SECTOR DISRUPTION - crisis in automotive, steel, chemical, textile, electronics; energy cost-driven shutdowns; raw material shortages affecting capacity

IRRELEVANT: sports, culture, food, travel, pure stock market commentary, central bank rate decisions without industrial impact, general consumer product launches.

Return ONLY a valid JSON object (no markdown, no explanation):
{"relevant": true/false, "confidence": 0.0-1.0, "signal_hint": "one sentence"}"""

PROMPT_TURN1_BATCH_SYSTEM = """You are an industrial news classifier for BIOS Signal Radar.

You will receive a JSON array of news articles. For each article, classify whether it belongs to one of these RELEVANT signal categories:

1. FACTORY & PRODUCTION MOVEMENT - factory relocation, closure, new plant, capacity change
2. WORKFORCE & RESTRUCTURING - mass layoffs (500+ people), workforce reduction, consolidation
3. STRATEGIC CORPORATE NEWS - major M&A, bankruptcy, outsourcing decisions, supply chain restructuring
4. INVESTMENT & TENDER - major CapEx announcements, industrial equipment tenders, government-backed factory investments
5. SECTOR DISRUPTION - crisis in automotive, steel, chemical, textile, electronics; energy cost-driven shutdowns

IRRELEVANT: sports, culture, food, travel, pure stock market commentary, central bank decisions without industrial impact.

Input: JSON array with "id" and "text" fields.
Return ONLY a valid JSON object (no markdown, no explanation):
{"results": [{"id": "...", "relevant": true/false, "confidence": 0.0-1.0, "signal_hint": "one sentence"}, ...]}"""

PROMPT_TURN2_SYSTEM = """You are a senior industrial intelligence analyst for BIOS Signal Radar.

This article was flagged as relevant because: "{signal_hint}"

Your task: Perform a deep analysis and produce a structured intelligence report.
Return ONLY a valid JSON object (no markdown, no explanation, no trailing text). Use null for unknown fields - NEVER invent data.

IMPORTANT — event_type MUST be exactly one of these values:
  relocation   = factory/production line moving from one location to another
  new_plant    = completely new facility being built (greenfield investment)
  expansion    = existing facility growing in capacity/headcount
  closure      = facility shutting down, capacity being eliminated
  tender       = procurement/contract/equipment purchase announcement
  layoff       = mass workforce reduction (500+ people)
  acquisition  = company being bought/merged/taken over
  restructuring = corporate reorganization, cost-cutting program
  supply_chain = supply chain disruption, shortage, logistics issue
  other        = does not fit any category above

JSON schema:
{{
  "event_type": "one of the 10 values above",
  "summary_tr": "Turkish 3-5 sentence summary explaining company, location, scale, and consequences",
  "company": "Main company name or null",
  "from_location": "Source location (city/country) or null",
  "to_location": "Target location (city/country) or null",
  "sector": "Automotive|Steel|Chemical|Textile|Electronics|Logistics|Energy|Aerospace|Pharmaceuticals|Other|null",
  "subsector": "Subsector detail or null",
  "timeline": "When this happens e.g. 2026 Q1, 2026-2027, by end of 2026, or null",
  "capex_eur": null,
  "jobs_impact": null,
  "line_type": "Affected production line type or null",
  "equipment_keywords": [],
  "signal_type": "positive|negative|neutral",
  "confidence": 0.0,
  "reasoning": "Why this was classified this way and which factors were decisive",
  "assumptions": []
}}"""


# ─── Ollama API Çağrısı ───────────────────────────────────────────────────────

def _extract_json_from_text(text: str) -> Optional[str]:
    """LLM çıktısından ilk geçerli JSON nesnesini veya dizisini çıkar."""
    # Markdown kod bloklarını temizle
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    
    # İlk { veya [ karakterinden başla
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        if start == -1:
            continue
        # Eşleşen kapanışı bul
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == start_char:
                depth += 1
            elif ch == end_char:
                depth -= 1
                if depth == 0:
                    candidate = text[start:i+1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        break
    return None


async def call_ollama(
    system: str,
    user: str,
    max_tokens: int = 1024,
) -> Optional[str]:
    """Ollama'nın /api/chat endpoint'ini kullanarak yerel Llama3 modeline istek gönder."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.1,   # Düşük sıcaklık → daha deterministik JSON
        },
    }

    async with SEMAPHORE:
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(
                        f"{OLLAMA_BASE_URL}/api/chat",
                        json=payload,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    raw_text = data.get("message", {}).get("content", "")
                    logger.debug(f"Ollama raw response: {raw_text[:300]!r}")
                    return _extract_json_from_text(raw_text) or raw_text
            except httpx.ReadTimeout:
                wait = 10 * (attempt + 1)
                logger.warning(f"Ollama timeout (attempt {attempt+1}), retrying in {wait}s...")
                await asyncio.sleep(wait)
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama HTTP error: {e.response.status_code} — {e.response.text[:200]}")
                return None
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                if attempt < 2:
                    await asyncio.sleep(5 * (attempt + 1))
                else:
                    return None
    return None


# ─── Turn 1 & Turn 2 ─────────────────────────────────────────────────────────

async def run_turn1(article_text: str) -> Optional[dict]:
    text = await call_ollama(
        system=PROMPT_TURN1_SYSTEM,
        user=f"NEWS TEXT (first 800 chars):\n{article_text[:800]}\n\nReturn JSON:",
        max_tokens=200,
    )
    logger.info(f"DEBUG Turn1 RAW response: {text!r}")
    if not text:
        return None
    return parse_json_safe(text)


async def run_turn1_batch(articles: list[dict]) -> dict[str, dict]:
    """
    Toplu Turn 1 kontrolü.
    articles: [{"id": "...", "text": "..."}, ...]
    Returns: { "id": {"relevant": True, "confidence": 0.9, ...}, ... }
    """
    if not articles:
        return {}

    payload = [{"id": a["id"], "text": a["text"][:800]} for a in articles]
    user_prompt = f"Evaluate these news articles:\n\n{json.dumps(payload, ensure_ascii=False)}"

    text = await call_ollama(
        system=PROMPT_TURN1_BATCH_SYSTEM,
        user=user_prompt,
        max_tokens=2000,
    )
    logger.info(f"DEBUG Batch RAW response: {text!r}")

    if not text:
        return {}

    parsed = parse_json_safe(text)
    if not parsed or "results" not in parsed:
        logger.warning("Turn1Batch parse failed or missing results array.")
        return {}

    return {res["id"]: res for res in parsed["results"]}


async def run_turn2(article_text: str, signal_hint: str) -> Optional[dict]:
    system = PROMPT_TURN2_SYSTEM.format(signal_hint=signal_hint)
    text = await call_ollama(
        system=system,
        user=f"ARTICLE TEXT:\n{article_text[:3000]}\n\nReturn JSON:",
        max_tokens=1500,
    )
    logger.info(f"DEBUG Turn2 RAW response: {text!r}")
    if not text:
        return None
    return parse_json_safe(text)


async def _translate_to_turkish(text: str) -> Optional[str]:
    if not text or not text.strip():
        return text
    prompt = (
        "Translate the following text to Turkish. "
        "Return ONLY the Turkish translation (no quotes, no markdown):\n\n"
        f"{text.strip()}"
    )
    translated = await call_ollama(
        system="You are a professional translator. Output plain Turkish text only.",
        user=prompt,
        max_tokens=250,
    )
    return (translated or "").strip() or text


async def _ensure_summary_tr(summary_tr: Optional[str]) -> Optional[str]:
    if not summary_tr:
        return summary_tr
    if not _LANGDETECT_OK:
        return summary_tr
    try:
        lang = detect(summary_tr[:500])
    except Exception:
        return summary_tr
    if lang == "tr":
        return summary_tr
    return await _translate_to_turkish(summary_tr)


# ─── Demo Seed Bypass ─────────────────────────────────────────────────────────

def _make_demo_result(article: dict) -> dict:
    """Demo modunda sahte AI sonucu döndür."""
    title_lower = (article.get("title") or "").lower()

    if any(kw in title_lower for kw in ["relocat", "move", "shift", "transfer", "taşı"]):
        event_type = "relocation"
    elif any(kw in title_lower for kw in ["close", "shut", "kapan"]):
        event_type = "closure"
    elif any(kw in title_lower for kw in ["expand", "new plant", "greenfield", "genişle"]):
        event_type = "expansion"
    elif any(kw in title_lower for kw in ["tender", "ihale", "contract"]):
        event_type = "tender"
    else:
        event_type = "other"

    return {
        "event_type": event_type,
        "summary_tr": f"Demo modu: {article.get('title', '')[:100]}. Bu haber otomatik olarak analiz edildi.",
        "company": None,
        "from_location": None,
        "to_location": None,
        "sector": None,
        "subsector": None,
        "timeline": None,
        "capex_eur": None,
        "jobs_impact": None,
        "line_type": None,
        "equipment_keywords": [],
        "signal_type": "neutral",
        "confidence": 0.5,
        "reasoning": "Demo modu — gerçek AI analizi devre dışı",
        "assumptions": [],
    }


# ─── Ana Pipeline ─────────────────────────────────────────────────────────────

async def process_article(article: dict) -> Optional[dict]:
    """
    2-turlu AI pipeline. (Tekil versiyon - Geriye dönük uyumluluk)
    Returns: AI analiz sonuçları dict veya None (alakasız / hatalı)
    """
    if DEMO_MODE:
        logger.debug(f"DEMO_MODE: bypassing AI for {article.get('title', '')[:50]}")
        return _make_demo_result(article)

    full_text = f"{article.get('title', '')}. {article.get('content', '')}"

    if len(full_text.strip()) < 30:
        return None

    # Tur 1: Alaka tespiti
    turn1 = await run_turn1(full_text)
    if not turn1:
        logger.warning(f"Turn1 parse failed: {article.get('title', '')[:50]}")
        return {"_failed": "turn1_parse_failed"}

    if not turn1.get("relevant"):
        logger.info(f"Irrelevant: {article.get('title', '')[:60]}")
        return None  # Tur 2 yapma

    signal_hint = turn1.get("signal_hint", "Industrial relocation signal")
    return await process_article_turn2(article, signal_hint)


async def process_article_turn2(article: dict, signal_hint: str) -> Optional[dict]:
    """Sadece Tur 2 analizini yapar."""
    if DEMO_MODE:
        return _make_demo_result(article)

    full_text = f"{article.get('title', '')}. {article.get('content', '')}"
    if len(full_text.strip()) < 30:
        return None

    # Tur 2: Tam analiz
    turn2 = await run_turn2(full_text, signal_hint)
    if not turn2:
        logger.warning(f"Turn2 parse failed: {article.get('title', '')[:50]}")
        return {"_failed": "turn2_parse_failed"}

    # Enforce Turkish summary (some models may ignore the prompt)
    try:
        turn2["summary_tr"] = await _ensure_summary_tr(turn2.get("summary_tr"))
    except Exception as e:
        logger.warning(f"summary_tr language enforcement failed: {e}")

    return turn2
