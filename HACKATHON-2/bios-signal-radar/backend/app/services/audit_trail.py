"""Audit Trail — Skor adım açıklama zinciri."""
from typing import Optional


def build_audit_trail(article: dict, score_result: dict) -> list[dict]:
    """
    4 adımlı audit trail üret.
    Returns: list of step dicts
    """
    c = score_result.get("components", {})
    a = score_result.get("adjustments", {})

    steps = []

    # ─── Adım 1: Alan Doluluk Kontrolü ───────────────────────────────────────
    field_checks = {
        "company":       article.get("company"),
        "from_location": article.get("from_location"),
        "to_location":   article.get("to_location"),
        "sector":        article.get("sector"),
        "event_type":    article.get("event_type"),
    }
    filled = [k for k, v in field_checks.items() if v and v != "other"]
    missing = [k for k, v in field_checks.items() if not v or v == "other"]

    steps.append({
        "step": 1,
        "title": "Alan Kontrolü",
        "detail": (
            " | ".join(f"{k}=✅" for k in filled) +
            (" | " if missing else "") +
            " | ".join(f"{k}=❌" for k in missing)
        ),
        "confidence": score_result.get("confidence", 0),
        "filled_count": len(filled),
        "total_fields": 5,
    })

    # ─── Adım 2: BIOS Bileşen Puanları ───────────────────────────────────────
    E = c.get("E", 0)
    A = c.get("A", 0)
    G = c.get("G", 0)
    T = c.get("T", 0)
    C = c.get("C", 0)

    steps.append({
        "step": 2,
        "title": "BIOS Bileşen Puanları",
        "detail": (
            f"E(Olay)={E}×0.30={E*0.30:.2f} | "
            f"A(Aktör)={A}×0.25={A*0.25:.2f} | "
            f"G(Coğrafya)={G}×0.20={G*0.20:.2f} | "
            f"T(Zaman)={T}×0.15={T*0.15:.2f} | "
            f"C(Kaynak)={C}×0.10={C*0.10:.3f}"
        ),
        "raw_score": score_result.get("raw_score", 0),
        "components": c,
    })

    # ─── Adım 3: Düzeltmeler ─────────────────────────────────────────────────
    adj_texts = []
    sect_mult = a.get("sector_mult", 1.0)
    if sect_mult != 1.0:
        adj_texts.append(f"Sektör×{sect_mult:.2f}")
    ind_bonus = a.get("industry_bonus", 0.0)
    if ind_bonus != 0.0:
        adj_texts.append(f"KaynakOdak+{ind_bonus:.1f}")
    fresh = a.get("freshness_bonus", 0)
    if fresh > 0:
        adj_texts.append(f"Freshness+{fresh:.0f}")
    if a.get("confidence_penalty"):
        adj_texts.append("Güven Cezası×0.50")
    delta = a.get("graph_delta", 0)
    if delta != 0:
        adj_texts.append(f"Graf{delta:+.0f}")

    steps.append({
        "step": 3,
        "title": "Düzeltmeler",
        "detail": " | ".join(adj_texts) if adj_texts else "Düzeltme uygulanmadı",
        "adjustments": a,
    })

    # ─── Adım 4: Nihai Skor ──────────────────────────────────────────────────
    steps.append({
        "step": 4,
        "title": "Nihai Skor",
        "detail": (
            f"Ham={score_result.get('raw_score', 0)} → "
            f"Düzeltmeli → Final={score_result.get('score_final', 0)} "
            f"({score_result.get('label', '?')})"
        ),
        "final_score": score_result.get("score_final", 0),
        "label": score_result.get("label"),
        "color": score_result.get("color"),
    })

    return steps
