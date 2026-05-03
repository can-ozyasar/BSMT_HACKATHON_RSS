import asyncio
import logging
from datetime import datetime, timezone

from app.services.ai_processor import call_ollama

logger = logging.getLogger("synapse_ai")

_SEMAPHORE = asyncio.Semaphore(1)  # keep light; this is optional enrichment


def _build_prompt(article: dict, neighbors: list[dict], features: dict) -> tuple[str, str]:
    system = (
        "Sen BIOS Signal Radar için 'Synapse AI' skorlayıcısın.\n"
        "Amaç: Bu haberi grafik ağındaki bağlamına göre 0-100 arası 'Synapse AI' skoru üretmek.\n"
        "Kurallar:\n"
        "- Her zaman Türkçe cevap ver.\n"
        "- Sadece verilen verilere dayan; uydurma.\n"
        "- Skor 0-100 tam sayı.\n"
        "- Çıktı SADECE JSON olsun (markdown yok).\n\n"
        "JSON Şeması:\n"
        "{\n"
        '  "synapse_ai_score": 0,\n'
        '  "reasoning_tr": "2-4 cümle kısa gerekçe",\n'
        '  "key_factors": ["madde", "madde"]\n'
        "}\n"
    )

    # Keep payload small to avoid timeouts.
    neighbor_compact = [
        {
            "id": n.get("id"),
            "company": n.get("company"),
            "event_type": n.get("event_type"),
            "signal_type": n.get("signal_type"),
            "score": n.get("score"),
            "relationship": n.get("relationship"),
            "reasons": n.get("reasons", [])[:4],
        }
        for n in (neighbors or [])[:6]
    ]

    user = (
        "Aşağıdaki veriyi kullanarak Synapse AI skoru üret.\n\n"
        f"HABER:\n"
        f"- id: {article.get('id')}\n"
        f"- başlık: {article.get('title')}\n"
        f"- şirket: {article.get('company')}\n"
        f"- lokasyon: {article.get('to_location') or article.get('from_location')}\n"
        f"- olay_tipi: {article.get('event_type')}\n"
        f"- sinyal: {article.get('signal_type')}\n"
        f"- BIOS_skor: {(article.get('bios_fit') or {}).get('score_final', 0)}\n"
        f"- özet_tr: {article.get('summary_tr')}\n\n"
        f"GRAF ÖZELLİKLERİ (deterministik):\n{features}\n\n"
        f"KOMŞU HABERLER (özet):\n{neighbor_compact}\n\n"
        "ÇIKTI:"
    )

    return system, user


async def compute_synapse_ai(article: dict, neighbors: list[dict], features: dict) -> dict | None:
    """
    Computes AI-based synapse score. Returns dict or None on failure.
    """
    system, user = _build_prompt(article, neighbors, features)

    async with _SEMAPHORE:
        try:
            text = await call_ollama(system=system, user=user, max_tokens=350)
            if not text:
                return None
            from app.utils.json_safe import parse_json_safe

            parsed = parse_json_safe(text)
            if not parsed:
                return None
            score = parsed.get("synapse_ai_score")
            if not isinstance(score, (int, float)):
                return None
            score_int = int(max(0, min(100, round(float(score)))))
            return {
                "synapse_ai_score": score_int,
                "reasoning_tr": (parsed.get("reasoning_tr") or "").strip(),
                "key_factors": parsed.get("key_factors") or [],
                "model": "ollama",
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.warning(f"Synapse AI compute failed: {e}")
            return None

