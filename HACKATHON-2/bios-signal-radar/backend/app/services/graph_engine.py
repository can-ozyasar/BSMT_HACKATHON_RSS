"""Graph Engine — Haber grafı inşası ve score propagation."""
import json
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger("graph_engine")

DATA_DIR = Path("data")
GRAPH_FILE = DATA_DIR / "graph.json"

POSITIVE_DELTA =  8.0   # Pozitif komşudan kazanç
NEGATIVE_DELTA = -15.0  # Negatif komşudan ceza


class GraphEngine:
    def build_graph_edges(self, articles: list[dict]) -> list[dict]:
        """
        Şirket ve lokasyon bazlı kenarlar oluştur.
        İki haber aynı şirkete/lokasyona sahipse → kenar var.
        """
        edges = []
        processed_ids = [a["id"] for a in articles if a.get("id")]

        for i, a1 in enumerate(articles):
            for a2 in articles[i + 1:]:
                reasons = []
                # Aynı şirket
                if (a1.get("company") and a2.get("company") and
                        a1["company"].lower() == a2["company"].lower()):
                    reasons.append("same_company")
                # Aynı to_location
                if (a1.get("to_location") and a2.get("to_location") and
                        a1["to_location"].lower() == a2["to_location"].lower()):
                    reasons.append("same_location")
                # Aynı sektör
                if (a1.get("sector") and a2.get("sector") and
                        a1["sector"].lower() == a2["sector"].lower()):
                    reasons.append("same_sector")
                # Aynı event_type (eğer ikisi de "other" değilse)
                if (a1.get("event_type") and a2.get("event_type") and
                        a1["event_type"] != "other" and
                        a1["event_type"] == a2["event_type"]):
                    reasons.append("same_event")

                if reasons:
                    # Sinyal tipi
                    s1 = a1.get("signal_type", "neutral")
                    s2 = a2.get("signal_type", "neutral")
                    relationship = f"{s1}_to_{s2}"

                    edges.append({
                        "source": a1["id"],
                        "target": a2["id"],
                        "reasons": reasons,
                        "relationship": relationship,
                        "signal_source": s1,
                        "signal_target": s2,
                    })

        return edges

    def propagate_scores(self, articles: list[dict], edges: list[dict]) -> dict[str, float]:
        """
        Her makale için komşu etkisini hesapla.
        Returns: {article_id: delta}
        """
        deltas: dict[str, float] = defaultdict(float)

        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            src_signal = edge.get("signal_source", "neutral")
            tgt_signal = edge.get("signal_target", "neutral")

            # Kaynak → Hedef etkisi
            if src_signal == "negative":
                deltas[tgt] += NEGATIVE_DELTA
            elif src_signal == "positive":
                deltas[tgt] += POSITIVE_DELTA

            # Hedef → Kaynak etkisi
            if tgt_signal == "negative":
                deltas[src] += NEGATIVE_DELTA
            elif tgt_signal == "positive":
                deltas[src] += POSITIVE_DELTA

        # Clamp: -20 ile +20 arası
        return {k: max(-20, min(20, v)) for k, v in deltas.items()}

    def get_neighbors(self, article_id: str, articles: list[dict], edges: list[dict]) -> list[dict]:
        """Bir makalenin komşu haberlerini döndür."""
        article_map = {a["id"]: a for a in articles}
        neighbors = []

        for edge in edges:
            neighbor_id = None
            if edge["source"] == article_id:
                neighbor_id = edge["target"]
            elif edge["target"] == article_id:
                neighbor_id = edge["source"]

            if neighbor_id and neighbor_id in article_map:
                neighbor = article_map[neighbor_id]
                bios = neighbor.get("bios_fit") or {}
                neighbors.append({
                    "id": neighbor_id,
                    "title": neighbor.get("title"),
                    "company": neighbor.get("company"),
                    "event_type": neighbor.get("event_type"),
                    "signal_type": neighbor.get("signal_type"),
                    "score": bios.get("score_final", 0),
                    "relationship": edge.get("relationship"),
                    "reasons": edge.get("reasons", []),
                })

        return neighbors

    def build_synapse_features(self, article_id: str, edges: list[dict], articles: list[dict]) -> dict:
        """
        Feature summary for AI synapse scoring (small + interpretable).
        """
        degree = 0
        same_company = 0
        same_location = 0
        same_sector = 0
        same_event = 0
        positive = 0
        negative = 0

        for e in edges:
            if e.get("source") == article_id or e.get("target") == article_id:
                degree += 1
                reasons = e.get("reasons", [])
                if "same_company" in reasons:
                    same_company += 1
                if "same_location" in reasons:
                    same_location += 1
                if "same_sector" in reasons:
                    same_sector += 1
                if "same_event" in reasons:
                    same_event += 1

                # Treat either side signals as neighborhood polarity
                if e.get("signal_source") == "positive" or e.get("signal_target") == "positive":
                    positive += 1
                if e.get("signal_source") == "negative" or e.get("signal_target") == "negative":
                    negative += 1

        return {
            "degree": degree,
            "same_company_edges": same_company,
            "same_location_edges": same_location,
            "same_sector_edges": same_sector,
            "same_event_edges": same_event,
            "positive_edge_count": positive,
            "negative_edge_count": negative,
            "node_count_total": len(articles or []),
            "edge_count_total": len(edges or []),
        }

    def calculate_synapse_score(self, article_id: str, edges: list[dict], articles: list[dict] = None) -> tuple[int, list[dict]]:
        """
        Grafik üzerindeki bağlantılara göre 'Synapse Skoru' (0-100) hesaplar.

        log1p bazlı bileşenler sayesinde yoğun graflarda doygunluk (100'e yapışma) önlenir.
        Teorik maksimum ~70 puan; final skor 0-100'e ölçeklenir.
        """
        breakdown: list[dict] = []
        base = 5.0
        breakdown.append({"reason": "Ağ Taban Puanı", "points": base, "type": "base"})

        article_map = {a["id"]: a for a in articles} if articles else {}
        from datetime import datetime, timezone
        import math

        neighbor_count = 0
        same_company = 0
        same_location = 0
        same_sector = 0
        same_event = 0
        positive_links = 0
        negative_links = 0
        recent_neighbors = 0

        for edge in edges:
            if edge["source"] == article_id or edge["target"] == article_id:
                neighbor_count += 1
                reasons = edge.get("reasons", [])
                is_source = edge["source"] == article_id
                neighbor_id = edge["target"] if is_source else edge["source"]

                signal = edge.get("signal_target") if is_source else edge.get("signal_source")

                if "same_company" in reasons:
                    same_company += 1
                if "same_location" in reasons:
                    same_location += 1
                if "same_sector" in reasons:
                    same_sector += 1
                if "same_event" in reasons:
                    same_event += 1

                if signal == "positive":
                    positive_links += 1
                elif signal == "negative":
                    negative_links += 1

                if neighbor_id in article_map:
                    n_article = article_map[neighbor_id]
                    pub_date = n_article.get("published_at")
                    if pub_date:
                        try:
                            pub = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                            age = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
                            if age < 48:
                                recent_neighbors += 1
                        except Exception:
                            pass

        # ── log1p bazlı bileşenler (sqrt yerine) — doygunluk önlenir ──────
        # Bağlantı yoğunluğu (max 25)
        conn = min(25.0, 8.0 * math.log1p(neighbor_count))
        breakdown.append({"reason": f"Bağlantı Yoğunluğu ({neighbor_count} bağ)", "points": round(conn, 1), "type": "connectivity"})

        # Anlamsal yakınlık — log1p ile sqrt'dan daha yavaş büyür (max 25)
        sem = (
            8.0 * math.log1p(same_company) +
            6.0 * math.log1p(same_location) +
            3.0 * math.log1p(same_event) +
            1.5 * math.log1p(same_sector)
        )
        sem = min(25.0, sem)
        breakdown.append({
            "reason": f"Anlamsal Yakınlık (şirket:{same_company}, lokasyon:{same_location}, olay:{same_event}, sektör:{same_sector})",
            "points": round(sem, 1),
            "type": "semantic",
        })

        # Momentum (max 8)
        mom = min(8.0, max(-8.0, 2.0 * positive_links - 1.5 * negative_links))
        breakdown.append({"reason": f"Momentum (poz:{positive_links}, neg:{negative_links})", "points": round(mom, 1), "type": "momentum"})

        # Tazelik (max 7)
        rec = min(7.0, 1.5 * recent_neighbors)
        breakdown.append({"reason": f"Tazelik (48s içinde komşu:{recent_neighbors})", "points": round(rec, 1), "type": "recency"})

        # Teorik max = 5+25+25+8+7 = 70; 0-100'e ölçekle
        raw_total = base + conn + sem + max(0.0, mom) + rec
        final_score = max(0, min(100, int(raw_total / 70.0 * 100.0 + 0.5)))
        breakdown.append({"reason": "Toplam", "points": final_score, "type": "total"})
        return final_score, breakdown

    def save(self, nodes: list[dict], edges: list[dict]):
        GRAPH_FILE.write_text(
            json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load(self) -> dict:
        if not GRAPH_FILE.exists():
            return {"nodes": [], "edges": []}
        try:
            return json.loads(GRAPH_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"nodes": [], "edges": []}


graph_engine = GraphEngine()
