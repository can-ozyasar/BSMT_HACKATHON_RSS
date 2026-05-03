"""Source Trust — Kaynak güveni ve endüstriyel odak skoru."""
from typing import Optional

SOURCE_REGISTRY: dict[str, dict] = {
    # Resmi/IR sayfaları
    "official": {"trust": 1.00, "focus": 1.00, "tier": "official"},
    # Saygın haber ajansları
    "reuters.com":        {"trust": 0.85, "focus": 1.00, "tier": "tier1"},
    "reuters":            {"trust": 0.85, "focus": 1.00, "tier": "tier1"},
    "bloomberg.com":      {"trust": 0.85, "focus": 1.00, "tier": "tier1"},
    "bloomberg":          {"trust": 0.85, "focus": 1.00, "tier": "tier1"},
    "ft.com":             {"trust": 0.85, "focus": 1.00, "tier": "tier1"},
    "wsj.com":            {"trust": 0.85, "focus": 1.00, "tier": "tier1"},
    "handelsblatt.com":   {"trust": 0.85, "focus": 1.10, "tier": "tier1"},
    "handelsblatt":       {"trust": 0.85, "focus": 1.10, "tier": "tier1"},
    # Sektörel yayınlar
    "just-auto.com":      {"trust": 0.70, "focus": 1.20, "tier": "sector"},
    "just-auto":          {"trust": 0.70, "focus": 1.20, "tier": "sector"},
    "industryweek.com":   {"trust": 0.70, "focus": 1.15, "tier": "sector"},
    "industryweek":       {"trust": 0.70, "focus": 1.15, "tier": "sector"},
    "manufacturing.net":  {"trust": 0.70, "focus": 1.15, "tier": "sector"},
    "automotive-news":    {"trust": 0.70, "focus": 1.20, "tier": "sector"},
    "autonews.com":       {"trust": 0.70, "focus": 1.20, "tier": "sector"},
    "plasticsnews.com":   {"trust": 0.70, "focus": 1.10, "tier": "sector"},
    # Genel haber
    "bbc.com":            {"trust": 0.55, "focus": 1.00, "tier": "general"},
    "bbc.co.uk":          {"trust": 0.55, "focus": 1.00, "tier": "general"},
    "cnn.com":            {"trust": 0.55, "focus": 1.00, "tier": "general"},
    "theguardian.com":    {"trust": 0.55, "focus": 1.00, "tier": "general"},
    "dw.com":             {"trust": 0.55, "focus": 1.05, "tier": "general"},
    # Blog/forum
    "reddit.com":         {"trust": 0.15, "focus": 1.00, "tier": "blog"},
    "medium.com":         {"trust": 0.20, "focus": 1.00, "tier": "blog"},
    "blog":               {"trust": 0.20, "focus": 1.00, "tier": "blog"},
}

DEFAULT = {"trust": 0.55, "focus": 1.00, "tier": "general"}


def get_enhanced_source_trust(url: str) -> dict:
    """URL'den trust × focus skoru döndür."""
    url_lower = url.lower()
    result = DEFAULT.copy()
    result["domain"] = url_lower

    for key, data in SOURCE_REGISTRY.items():
        if key in url_lower:
            result = {**data, "domain": key}
            break

    result["combined"] = round(result["trust"] * result["focus"], 3)
    return result
