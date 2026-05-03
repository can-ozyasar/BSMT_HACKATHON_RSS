"""Entity normalizasyonu — şirket ve lokasyon canonical adları."""
from typing import Optional
import re

# Şirket kanonik adları (alias → canonical)
COMPANY_CANONICAL: dict[str, str] = {
    # BMW grubu
    "bmw ag": "BMW",
    "bmw group": "BMW",
    "bayerische motoren werke": "BMW",
    # Volkswagen grubu
    "volkswagen ag": "Volkswagen",
    "vw ag": "Volkswagen",
    "vw group": "Volkswagen",
    "volkswagen group": "Volkswagen",
    # Mercedes-Benz
    "daimler ag": "Mercedes-Benz",
    "daimler": "Mercedes-Benz",
    "mercedes benz": "Mercedes-Benz",
    "mercedes-benz group": "Mercedes-Benz",
    # Stellantis
    "fca": "Stellantis",
    "fiat chrysler": "Stellantis",
    "psa group": "Stellantis",
    # Siemens
    "siemens ag": "Siemens",
    # BASF
    "basf se": "BASF",
    # Renault
    "renault group": "Renault",
    "renault sa": "Renault",
    # Bosch
    "robert bosch": "Bosch",
    "bosch gmbh": "Bosch",
    # Continental
    "continental ag": "Continental",
    # Altri
    "thyssenkrupp ag": "ThyssenKrupp",
    "thyssen krupp": "ThyssenKrupp",
    "airbus se": "Airbus",
    "airbus group": "Airbus",
    "volvo group": "Volvo",
    "volvo cars": "Volvo",
    "ab volvo": "Volvo",
    "stellantis nv": "Stellantis",
}

# Lokasyon kanonik adları
LOCATION_CANONICAL: dict[str, str] = {
    "munich": "München",
    "muenchen": "München",
    "münchen": "München",
    "warsaw": "Warszawa",
    "wroclaw": "Wrocław",
    "prague": "Praha",
    "bratislava": "Bratislava",
    "budapest": "Budapest",
    "bucharest": "București",
    "sofia": "Sofiya",
    "zagreb": "Zagreb",
    "belgrade": "Beograd",
    "debrecen": "Debrecen",
    "cologne": "Köln",
    "koeln": "Köln",
    "frankfurt am main": "Frankfurt",
    "frankfurt a.m.": "Frankfurt",
}


def normalize_company(raw: Optional[str]) -> Optional[str]:
    """'BMW AG' → 'BMW'"""
    if not raw:
        return None
    lower = raw.lower().strip()
    for alias, canonical in COMPANY_CANONICAL.items():
        if alias in lower:
            return canonical
    # Şirket tipi eklerini kaldır
    cleaned = re.sub(
        r'\b(ag|gmbh|se|plc|inc|ltd|sa|nv|bv|srl|spa|corp|co\.|group)\b',
        '', raw, flags=re.IGNORECASE
    ).strip()
    return cleaned if cleaned else raw


def normalize_location(raw: Optional[str]) -> Optional[str]:
    """'Munich' → 'München'"""
    if not raw:
        return None
    lower = raw.lower().strip()
    for alias, canonical in LOCATION_CANONICAL.items():
        if alias in lower:
            return canonical
    return raw


def normalize_article_entities(article: dict) -> dict:
    """Article içindeki tüm entity alanlarını normalize et."""
    article["company"] = normalize_company(article.get("company"))
    article["from_location"] = normalize_location(article.get("from_location"))
    article["to_location"] = normalize_location(article.get("to_location"))
    return article
