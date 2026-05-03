"""Anomaly Engine — Spike detection (6 saatlik pencere)."""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("anomaly_engine")

DATA_DIR = Path("data")
HISTORY_FILE = DATA_DIR / "anomaly_history.json"


class AnomalyEngine:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        if not HISTORY_FILE.exists():
            HISTORY_FILE.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self, history: list[dict]):
        HISTORY_FILE.write_text(
            json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def record(self, company: Optional[str], location: Optional[str],
               article_id: str, timestamp: Optional[str] = None):
        """Haberi anomali geçmişine kaydet."""
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        history = self._load()

        if company:
            history.append({
                "entity": company, "entity_type": "company",
                "article_id": article_id, "timestamp": ts
            })
        if location:
            history.append({
                "entity": location, "entity_type": "location",
                "article_id": article_id, "timestamp": ts
            })

        # 30 günden eski kayıtları temizle
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        history = [h for h in history if h.get("timestamp", "") >= cutoff]
        self._save(history)

    def detect(
        self,
        window_hours: int = 6,
        baseline_days: int = 7,
        spike_threshold: float = 4.0,
    ) -> list[dict]:
        """Tüm entity'ler için spike'ları tespit et."""
        now = datetime.now(timezone.utc)
        window_start = (now - timedelta(hours=window_hours)).isoformat()
        baseline_start = (now - timedelta(days=baseline_days)).isoformat()

        history = self._load()

        # Entity başına sayım
        from collections import defaultdict
        recent_counts: dict = defaultdict(lambda: {"count": 0, "articles": []})
        baseline_counts: dict = defaultdict(int)

        for record in history:
            entity_key = f"{record['entity_type']}:{record['entity']}"
            ts = record.get("timestamp", "")
            if ts >= window_start:
                recent_counts[entity_key]["count"] += 1
                recent_counts[entity_key]["articles"].append(record["article_id"])
            if ts >= baseline_start:
                baseline_counts[entity_key] += 1

        anomalies = []
        for entity_key, data in recent_counts.items():
            entity_type, entity = entity_key.split(":", 1)
            baseline_total = baseline_counts.get(entity_key, data["count"])
            baseline_per_window = (baseline_total / baseline_days) * (window_hours / 24)
            if baseline_per_window < 0.5:
                baseline_per_window = 0.5  # Minimum baseline

            multiplier = data["count"] / baseline_per_window

            if multiplier >= spike_threshold:
                anomalies.append({
                    "entity": entity,
                    "entity_type": entity_type,
                    "article_count_recent": data["count"],
                    "article_count_baseline": round(baseline_per_window, 1),
                    "multiplier": round(multiplier, 1),
                    "threshold": spike_threshold,
                    "detected_at": now.isoformat(),
                    "related_article_ids": list(set(data["articles"])),
                })

        anomalies.sort(key=lambda a: a["multiplier"], reverse=True)
        return anomalies


anomaly_engine = AnomalyEngine()
