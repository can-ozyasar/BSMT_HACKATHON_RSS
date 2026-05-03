"""BIOS-Fit Skor Motoru.

Bu implementasyon `md/Hackathon_Yarisma_Raporu.md` bölüm 7.4 ile uyumludur:

Score = 100 × (0.30·E + 0.25·A + 0.20·G + 0.15·T + 0.10·C)

Confidence < 0.40 ise Score × 0.50 uygulanır ve tam sayıya yuvarlanır.
"""
from typing import Optional
from dataclasses import dataclass, field

from app.services.source_trust import get_enhanced_source_trust


# ─── Bileşen Tabloları ────────────────────────────────────────────────────────

EVENT_TYPE_SCORES: dict[str, float] = {
    # Core types (documented)
    "relocation":    1.00,
    "new_plant":     0.90,
    "expansion":     0.75,
    "tender":        0.55,
    "closure":       0.45,
    # Extended types returned by Ollama Turn2
    "layoff":        0.45,   # Same tier as closure — workforce reduction signal
    "acquisition":   0.65,   # M&A — between tender and expansion
    "restructuring": 0.50,   # Strategic change — moderate signal
    "supply_chain":  0.55,   # Supply chain disruption — same as tender
    "other":         0.10,
}

EUROPE_CORE: set[str] = {
    "germany", "france", "italy", "spain", "poland", "netherlands", "belgium",
    "sweden", "austria", "czech republic", "czechia", "romania", "hungary",
    "slovakia", "portugal", "greece", "finland", "denmark", "croatia", "bulgaria",
    "united kingdom", "uk", "england", "turkey", "türkiye", "serbia", "norway",
    "switzerland", "albania", "north macedonia", "moldova", "ukraine", "estonia",
    "latvia", "lithuania", "luxembourg", "malta", "cyprus", "ireland", "slovenia",
    "münchen", "munich", "berlin", "frankfurt", "hamburg", "cologne", "köln",
    "paris", "lyon", "milan", "madrid", "barcelona", "warsaw", "wroclaw",
    "krakow", "prague", "bratislava", "budapest", "bucharest", "sofia",
    "zagreb", "belgrade", "beograd", "debrecen", "istanbul", "ankara",
    # Turkey regions/cities (common Turkish news wording)
    "sakarya", "adapazarı", "adapazari", "kocaeli", "bursa", "izmit",
    "konya", "kayseri", "sivas", "eskişehir", "eskisehir",
    "central anatolia", "iç anadolu", "ic anadolu", "anatolia",
}

EUROPE_NEIGHBORS: set[str] = {
    "russia", "kazakhstan", "morocco", "algeria", "tunisia", "libya",
    "egypt", "georgia", "armenia", "azerbaijan", "israel", "lebanon",
}

SCORE_THRESHOLDS = [
    (80, "Yüksek Fırsat", "green",  "reach_out"),
    (65, "İzlenecek",     "blue",   "watchlist"),
    (50, "Şartlı İlgi",   "yellow", "monitor"),
    (0,  "Düşük Alaka",   "gray",   "archive"),
]


# ─── Bileşen Fonksiyonları ────────────────────────────────────────────────────

def score_event_type(event_type: Optional[str]) -> float:
    return EVENT_TYPE_SCORES.get(event_type or "other", 0.10)


def score_actor_clarity(company, from_loc, to_loc, sector) -> float:
    score = 0.0
    if company:   score += 0.40
    if from_loc:  score += 0.25
    if to_loc:    score += 0.25
    if sector:    score += 0.10
    return round(score, 2)


def score_geography(from_loc, to_loc) -> float:
    locs = [l.lower() for l in [from_loc, to_loc] if l]
    if not locs:
        return 0.0
    in_core  = sum(1 for l in locs if any(c in l for c in EUROPE_CORE))
    in_neigh = sum(1 for l in locs if any(n in l for n in EUROPE_NEIGHBORS))
    if in_core == len(locs):   return 1.00
    elif in_core >= 1:         return 0.75
    elif in_neigh >= 1:        return 0.50
    return 0.10


def score_timeline(timeline: Optional[str]) -> float:
    if not timeline:
        return 0.20
    tl = timeline.lower()
    NEAR = ["q1", "q2", "this year", "2025", "2026 q1", "2026 q2",
            "announced", "imminent", "next month", "coming months"]
    MID  = ["next year", "2026", "2027 q1", "2026 q3", "2026 q4",
            # Range formats like "2025-2026", "2026-2027"
            "2025-2026", "2026-2027", "2024-2026", "2025-2027"]
    FAR  = ["2028", "2029", "2030", "long-term", "multi-year",
            "2027-2028", "2027-2030", "2028-2030"]
    for kw in NEAR:
        if kw in tl: return 1.00
    for kw in MID:
        if kw in tl: return 0.70
    for kw in FAR:
        if kw in tl: return 0.40
    # Fallback: detect any year-range pattern like "YYYY-YYYY"
    import re
    range_match = re.search(r'(20\d\d)-(20\d\d)', tl)
    if range_match:
        end_year = int(range_match.group(2))
        if end_year <= 2027: return 0.70
        if end_year <= 2030: return 0.40
    return 0.20


def calculate_confidence(company, from_loc, to_loc, sector, event_type) -> float:
    fields = [company, from_loc, to_loc, sector, event_type]
    filled = sum(1 for f in fields if f and f not in ("other", ""))
    return round(filled / 5, 2)


def get_score_label(score: int) -> tuple[str, str, str]:
    for threshold, label, color, action in SCORE_THRESHOLDS:
        if score >= threshold:
            return label, color, action
    return "Düşük Alaka", "gray", "archive"


# ─── Ana Skor Fonksiyonu ─────────────────────────────────────────────────────

def calculate_bios_score(article: dict, graph_delta: float = 0.0) -> dict:
    """
    BIOS-Fit skor hesabı.
    Returns: tam skor dict (score, components, adjustments, label, color, audit_trail)
    """
    event_type    = article.get("event_type")
    company       = article.get("company")
    from_location = article.get("from_location")
    to_location   = article.get("to_location")
    sector        = article.get("sector")
    timeline      = article.get("timeline")
    source_url    = article.get("source_url") or article.get("original_url") or ""

    # Bileşen puanları
    E = score_event_type(event_type)
    A = score_actor_clarity(company, from_location, to_location, sector)
    G = score_geography(from_location, to_location)
    T = score_timeline(timeline)

    trust_data = get_enhanced_source_trust(source_url)
    C = trust_data["trust"]
    C_focus = trust_data["focus"]

    # Ham skor
    raw = 100 * (0.30 * E + 0.25 * A + 0.20 * G + 0.15 * T + 0.10 * C)

    # Güven
    confidence = calculate_confidence(company, from_location, to_location, sector, event_type)

    # Math.round() davranışı: .5 her zaman yukarı yuvarlanır (banker's rounding değil).
    final = int(raw + 0.5)
    if confidence < 0.40:
        final = int(final * 0.50 + 0.5)
    final = max(0, min(100, final))
    label, color, action = get_score_label(final)

    return {
        "score":       final,
        "score_final": final,
        "raw_score":   round(raw, 2),
        "confidence":  confidence,
        "components": {"E": E, "A": A, "G": G, "T": T, "C": C},
        "adjustments": {
            "sector_mult":         1.0,
            "industry_focus":      C_focus,
            "industry_bonus":      0.0,
            "freshness_bonus":     0.0,
            "confidence_penalty":  confidence < 0.40,
            "graph_delta":         0.0,
        },
        "label":  label,
        "color":  color,
        "action": action,
        "source_tier": trust_data.get("tier", "general"),
    }
