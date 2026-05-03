"""
Test Pipeline — 2 Fake Article Scoring Test
==========================================
Runs two articles through the full Turn1 → Turn2 → Scorer pipeline
and prints a detailed report so you can see exactly how scoring works.

Usage (from the backend directory with venv active):
    python3 scripts/test_pipeline.py
"""
import asyncio
import json
import sys
import os

# Backend root must be in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_processor import run_turn1, run_turn2
from app.services.scorer import calculate_bios_score
from app.services.audit_trail import build_audit_trail

# ─── Test Articles ────────────────────────────────────────────────────────────

TEST_ARTICLES = [
    {
        "id": "test_001",
        "title": "Bosch closes Stuttgart gasoline engine plant, moves production to Lodz",
        "content": (
            "Robert Bosch GmbH announced on Thursday that it will permanently close its gasoline fuel "
            "injector manufacturing plant in Stuttgart, Germany, by the end of Q3 2026. The closure affects "
            "2,200 workers. Production of the affected components will be relocated to Bosch's existing "
            "facility in Łódź, Poland, where the company plans to invest €320 million to expand capacity "
            "and upgrade automation lines. The decision is driven by falling demand for combustion engine "
            "parts as European automakers accelerate their EV transition."
        ),
        "source_url": "https://www.reuters.com",
        "source_name": "Reuters",
        "published_at": "2026-05-03T06:00:00Z",
        "label": "INDUSTRIAL ",
    },
    {
        "id": "test_002",
        "title": "Siemens AG Resmi Basın Bülteni: Münih Endüstriyel Otomasyon Hattı Bursa'ya Taşınıyor",
        "content": (
          "  Siemens AG, küresel kapasite optimizasyonu stratejisi doğrultusunda, Almanya'nın Münih kentindeki endüstriyel otomasyon kontrol üniteleri üretim hattını tamamen kapatarak, bu hattı Türkiye'deki Bursa tesislerine taşıma kararı aldığını duyurdu. Şirketin yatırımcı ilişkileri sayfasından yapılan resmi açıklamaya göre, ekipmanların de-montaj ve transfer süreçleri önümüzdeki ay (Haziran 2026) içinde fiilen başlayacak. Endüstriyel otomasyon sektörüne hizmet veren bu hattın taşınmasıyla, hedeflenen kapasite artışı Avrupa sınırları içerisinde optimize edilmiş olacak. "
        ),
        "source_url": "https://www.bbc.co.uk",
        "source_name": "BBC",
        "published_at": "2026-05-03T08:00:00Z",
        "label": "relocation ",
    },
]

# ─── Runner ───────────────────────────────────────────────────────────────────

def print_separator(char="─", width=70):
    print(char * width)

def print_score_bar(score: int) -> str:
    filled = score // 5
    bar = "█" * filled + "░" * (20 - filled)
    return f"[{bar}] {score}/100"

async def run_test(article: dict, index: int):
    print_separator("═")
    print(f"  TEST {index}: {article['label']}")
    print_separator("═")
    print(f"  Title   : {article['title']}")
    print(f"  Source  : {article['source_name']} ({article['source_url']})")
    print()

    # ── Turn 1
    print("  ── TURN 1: Relevance Filter ──────────────────────────────────")
    full_text = f"{article['title']}. {article['content']}"
    turn1 = await run_turn1(full_text)

    if not turn1:
        print("  ❌ Turn 1 FAILED — could not parse AI response (Ollama down?)")
        print()
        return

    relevant = turn1.get("relevant", False)
    t1_conf  = turn1.get("confidence", 0)
    hint     = turn1.get("signal_hint", "—")

    status = "✅ RELEVANT" if relevant else "🚫 FILTERED OUT"
    print(f"  Result    : {status}")
    print(f"  Confidence: {t1_conf:.0%}")
    print(f"  Hint      : {hint}")

    if not relevant:
        print()
        print("  ► Article was filtered in Turn 1. No AI analysis, no score assigned.")
        print("  ► This is correct behaviour — saves LLM cost on irrelevant news.")
        print()
        return

    # ── Turn 2
    print()
    print("  ── TURN 2: Full Analysis ─────────────────────────────────────")
    turn2 = await run_turn2(full_text, hint)

    if not turn2:
        print("  ❌ Turn 2 FAILED — could not parse AI response")
        print()
        return

    print(f"  event_type   : {turn2.get('event_type')}")
    print(f"  company      : {turn2.get('company')}")
    print(f"  from_location: {turn2.get('from_location')}")
    print(f"  to_location  : {turn2.get('to_location')}")
    print(f"  sector       : {turn2.get('sector')}")
    print(f"  timeline     : {turn2.get('timeline')}")
    print(f"  jobs_impact  : {turn2.get('jobs_impact')}")
    print(f"  capex_eur    : {turn2.get('capex_eur')}")
    print(f"  signal_type  : {turn2.get('signal_type')}")
    print(f"  confidence   : {turn2.get('confidence')}")
    print(f"  reasoning    : {turn2.get('reasoning')}")

    # ── Scoring
    print()
    print("  ── BIOS-FIT SCORE ────────────────────────────────────────────")
    merged = {**article, **turn2}
    score_result = calculate_bios_score(merged, graph_delta=0.0)
    audit_steps  = build_audit_trail(merged, score_result)

    final = score_result["score_final"]
    label = score_result["label"]
    color = score_result["color"]
    c     = score_result["components"]

    color_emoji = {"green": "🟢", "blue": "🔵", "yellow": "🟡", "gray": "⚫"}.get(color, "⚪")

    print(f"  {color_emoji} Score  : {print_score_bar(final)}")
    print(f"  Label  : {label}")
    print(f"  Raw    : {score_result['raw_score']}")
    print()
    print("  Components:")
    print(f"    E (Event Type) = {c['E']} × 0.30 = {c['E']*0.30:.3f}")
    print(f"    A (Actor)      = {c['A']} × 0.25 = {c['A']*0.25:.3f}")
    print(f"    G (Geography)  = {c['G']} × 0.20 = {c['G']*0.20:.3f}")
    print(f"    T (Timeline)   = {c['T']} × 0.15 = {c['T']*0.15:.3f}")
    print(f"    C (Source)     = {c['C']} × 0.10 = {c['C']*0.10:.3f}")
    print()
    print("  Adjustments:")
    adj = score_result["adjustments"]
    print(f"    sector_mult    = {adj.get('sector_mult', 1.0)}")
    print(f"    industry_bonus = {adj.get('industry_bonus', 0.0)}")
    print(f"    freshness_bonus= {adj.get('freshness_bonus', 0.0)}")
    print(f"    conf_penalty   = {adj.get('confidence_penalty', False)}")
    print(f"    graph_delta    = {adj.get('graph_delta', 0.0)}")
    print()
    print("  Audit Trail:")
    for step in audit_steps:
        print(f"    Step {step['step']}: {step['title']}")
        print(f"           {step['detail']}")
    print()


async def main():
    print()
    print("  BIOS Signal Radar — Pipeline Test")
    print("  2 Articles: 1 Industrial + 1 Irrelevant")
    print()
    print("  NOTE: This requires Ollama running with llama3.")
    print("        If Ollama is not running, Turn 1 will fail.")
    print()

    for i, article in enumerate(TEST_ARTICLES, 1):
        await run_test(article, i)

    print_separator("═")
    print("  TEST COMPLETE")
    print_separator("═")
    print()


if __name__ == "__main__":
    asyncio.run(main())
