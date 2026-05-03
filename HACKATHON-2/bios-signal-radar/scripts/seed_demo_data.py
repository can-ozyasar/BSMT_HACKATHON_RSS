import os
import json
import uuid
from pathlib import Path

# Makaleler
ARTICLES = [
    {
        "id": "demo-bmw-debrecen",
        "title": "BMW Group announces €2B investment in Debrecen, Hungary for Neue Klasse EV production",
        "original_url": "https://www.reuters.com/business/autos-transportation/bmw-invest-2-bln-euros-hungary-battery-plant-2023-11-20/",
        "source_id": "rss_reuters",
        "source_name": "Reuters",
        "source_url": "https://www.reuters.com",
        "published_at": "2026-05-02T08:30:00Z",
        "fetched_at": "2026-05-02T09:00:00Z",
        "language": "en",
        "raw_hash": "a1b2c3d4e5f6g7h8",
        "content_preview": "BMW is expanding its European footprint with a massive €2B investment in Debrecen...",
        "analysis_status": "processed",
        "event_type": "new_plant",
        "summary_tr": "BMW, Macaristan'ın Debrecen kentinde elektrikli araç üretimi için 2 milyar Euro'luk yeni bir batarya fabrikası kuracağını duyurdu. Tesis 2026'da faaliyete geçecek.",
        "company": "BMW",
        "from_location": None,
        "to_location": "Debrecen",
        "sector": "Automotive",
        "timeline": "2026",
        "signal_type": "positive",
        "ai_confidence": 0.95,
        "has_anomaly": False,
        "bios_fit": {
            "score": 99,
            "score_final": 99,
            "raw_score": 99.0,
            "confidence": 1.0,
            "color": "green",
            "label": "Yüksek Fırsat",
            "action": "reach_out"
        }
    },
    {
        "id": "demo-basf-ludwigshafen",
        "title": "BASF to shut down several plants at Ludwigshafen site, cutting 2,600 jobs globally",
        "original_url": "https://www.handelsblatt.com/basf-closure",
        "source_id": "rss_handelsblatt",
        "source_name": "Handelsblatt",
        "source_url": "https://www.handelsblatt.com",
        "published_at": "2026-05-01T14:15:00Z",
        "fetched_at": "2026-05-02T09:00:00Z",
        "language": "en",
        "raw_hash": "h8g7f6e5d4c3b2a1",
        "content_preview": "Chemical giant BASF is restructuring its European operations due to high energy costs...",
        "analysis_status": "processed",
        "event_type": "closure",
        "summary_tr": "Kimya devi BASF, yüksek enerji maliyetleri nedeniyle Ludwigshafen'daki bazı üretim tesislerini kapatacağını ve küresel çapta 2.600 kişiyi işten çıkaracağını açıkladı.",
        "company": "BASF",
        "from_location": "Ludwigshafen",
        "to_location": None,
        "sector": "Chemicals",
        "timeline": "Q4 2026",
        "signal_type": "negative",
        "ai_confidence": 0.92,
        "has_anomaly": True,
        "anomaly_multiplier": 5.2,
        "bios_fit": {
            "score": 88,
            "score_final": 88,
            "raw_score": 88.0,
            "confidence": 0.8,
            "color": "green",
            "label": "Yüksek Fırsat",
            "action": "reach_out"
        }
    },
    {
        "id": "demo-siemens-prague",
        "title": "Siemens relocates regional headquarters from Munich to Prague",
        "original_url": "https://www.industryweek.com/siemens",
        "source_id": "rss_industryweek",
        "source_name": "IndustryWeek",
        "source_url": "https://www.industryweek.com",
        "published_at": "2026-05-02T10:00:00Z",
        "fetched_at": "2026-05-02T10:15:00Z",
        "language": "en",
        "raw_hash": "z1x2c3v4b5n6m7",
        "content_preview": "In a strategic shift, Siemens is moving its regional administrative hub to Prague...",
        "analysis_status": "processed",
        "event_type": "relocation",
        "summary_tr": "Siemens, bölgesel yönetim merkezini maliyetleri düşürmek amacıyla Münih'ten Prag'a taşıyor.",
        "company": "Siemens",
        "from_location": "München",
        "to_location": "Praha",
        "sector": "Electronics",
        "timeline": "2027 Q1",
        "signal_type": "neutral",
        "ai_confidence": 0.85,
        "has_anomaly": False,
        "bios_fit": {
            "score": 76,
            "score_final": 76,
            "raw_score": 76.0,
            "confidence": 1.0,
            "color": "blue",
            "label": "İzlenecek",
            "action": "watchlist"
        }
    }
]

# RSS Kaynakları
SOURCES = [
    {
        "id": "rss_reuters",
        "url": "https://www.reuters.com/tools/rss/business",
        "name": "Reuters Business",
        "status": "active",
        "added_at": "2026-05-01T00:00:00Z"
    },
    {
        "id": "rss_handelsblatt",
        "url": "https://www.handelsblatt.com/contentexport/feed/unternehmen",
        "name": "Handelsblatt Unternehmen",
        "status": "active",
        "added_at": "2026-05-01T00:00:00Z"
    }
]

def main():
    base_dir = Path(__file__).parent.parent
    seed_dir = base_dir / "data" / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    
    (seed_dir / "seed_articles.json").write_text(json.dumps(ARTICLES, ensure_ascii=False, indent=2), encoding="utf-8")
    (seed_dir / "seed_rss_sources.json").write_text(json.dumps(SOURCES, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Seed verileri oluşturuldu.")

if __name__ == "__main__":
    main()
