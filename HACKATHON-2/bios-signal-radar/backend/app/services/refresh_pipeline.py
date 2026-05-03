"""Ana refresh pipeline — tüm servisleri orkestre eder."""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.services.collector import collect_all
from app.services.normalizer import normalize
from app.services.entity_norm import normalize_article_entities
from app.services.ai_processor import process_article, process_article_turn2, run_turn1_batch
from app.services.scorer import calculate_bios_score
from app.services.audit_trail import build_audit_trail
from app.services.anomaly_engine import anomaly_engine
from app.services.graph_engine import graph_engine
from app.storage.rss_store import rss_store
from app.storage.articles_store import articles_store
from app.storage.dedup_store import dedup_store, simhash_store, DedupStore


def _generate_auto_questions(article: dict):
    """İşlenen haberden otomatik RAG soruları üret ve kaydet."""
    try:
        from app.routers.rag import save_auto_question
        company = article.get("company")
        sector = article.get("sector")
        to_loc = article.get("to_location")
        from_loc = article.get("from_location")
        event_type = article.get("event_type", "other")

        event_labels = {
            "relocation": "taşınma", "closure": "kapanış",
            "expansion": "genişleme", "new_plant": "yeni tesis açılışı",
            "tender": "ihale", "other": "gelişme",
        }
        label = event_labels.get(event_type, "gelişme")

        if company:
            save_auto_question(f"{company} hakkında son gelişmeler neler?")
        if company and (from_loc or to_loc):
            route = f"{from_loc or '?'} → {to_loc or '?'}"
            save_auto_question(f"{company} neden {route} taşınıyor?")
        if sector:
            save_auto_question(f"{sector} sektöründeki son {label} haberleri neler?")
        if to_loc:
            save_auto_question(f"{to_loc} bölgesindeki endüstriyel yatırımlar neler?")
    except Exception:
        pass

logger = logging.getLogger("refresh_pipeline")


async def run_refresh(source_ids: list[str] | None = None) -> dict:
    """
    Tam refresh pipeline.
    1. RSS çek
    2. Normalize
    3. Dedup
    4. AI işle
    5. Skor hesapla
    6. Kaydet
    7. Graf güncelle
    8. Anomali tespit
    """
    start = datetime.now(timezone.utc)

    # Kaynakları al
    all_sources = rss_store.list_active()
    if source_ids:
        sources = [s for s in all_sources if s["id"] in source_ids]
    else:
        sources = all_sources

    if not sources:
        return {"fetched": 0, "new": 0, "duplicates": 0, "errors": 0, "duration_seconds": 0}

    # 1. RSS Çek
    logger.info(f"Fetching from {len(sources)} sources...")
    raw_articles, fetch_errors = await collect_all(sources)
    logger.info(f"Fetched {len(raw_articles)} raw articles, {len(fetch_errors)} source errors")

    # Hatalı kaynakları işaretle
    for source_id, error_msg in fetch_errors.items():
        await rss_store.update_status(source_id, "error", error_message=error_msg)

    # Başarılı kaynakları güncelle
    successful_ids = set(s["id"] for s in sources) - set(fetch_errors.keys())
    for source_id in successful_ids:
        await rss_store.update_status(
            source_id, "active",
            last_fetched_at=datetime.now(timezone.utc).isoformat()
        )

    stats = {"fetched": len(raw_articles), "new": 0, "duplicates": 0, "errors": 0, "keyword_filtered": 0}
    new_articles = []

    # ─── Keyword Pre-Filter Set ───────────────────────────────────────────────
    # These keywords are checked against title+content BEFORE sending to AI.
    # Any article matching at least one keyword passes to AI; others are dropped.
    # This eliminates ~75-80% of irrelevant articles with zero API cost.
    SIGNAL_KEYWORDS = [
        # Factory / Production
        "factory", "plant", "facility", "fabrik", "werk", "anlage", "produktion",
        "manufacturing", "assembly", "production line", "greenfield", "brownfield",
        "closure", "closing", "shutdown", "kapan", "schließ",
        "relocation", "move", "transfer", "taşı", "verlager",
        "expansion", "invest", "yatırım", "investition", "capex",
        "gigafactory", "megafactory", "supply chain", "logistics",
        # Layoffs
        "layoff", "redundan", "retrench", "job cut", "workforce reduction",
        "işten çıkar", "küçült", "stellenabbau", "entlassung",
        "personnel", "employment", "istihdam",
        # M&A / Restructuring
        "merger", "acquisition", "takeover", "birleş", "satın al",
        "restructur", "yeniden yapı", "spin-off", "divestit",
        "bankruptcy", "insolvenc", "iflas", "insolven",
        "strategic", "partnership", "iş birliği", "cooperation",
        # Sectors & Tech
        "automotive", "steel", "otomotiv", "stahl", "chemical", "textile",
        "semiconductor", "electronics", "aerospace", "defense",
        "battery", "ev", "electric vehicle", "energy", "renewable",
        "hydrogen", "solar", "wind", "automation", "robotics",
        "ai", "digital transformation", "industry 4.0", "smart factory",
        # Supply chain
        "supply chain", "tedarik", "lieferkette", "shortage", "kıtlık",
        "material", "raw", "hizmet", "servis",
        # Tender & Business
        "tender", "ihale", "ausschreibung", "contract award",
        "revenue", "profit", "loss", "gelir", "kâr", "zarar",
        "growth", "büyüme", "decline", "daralma",
    ]

    def keyword_passes(article: dict) -> bool:
        haystack = (article.get("title", "") + " " + article.get("content", "")).lower()
        return any(kw in haystack for kw in SIGNAL_KEYWORDS)

    # 2. Ön işleme ve Dedup
    articles_to_process = []
    
    for raw in raw_articles:
        try:
            normalized = normalize(raw)
            if not normalized:
                continue

            url_hash = DedupStore.make_hash(
                normalized.get("original_url", ""),
                normalized.get("title", "")
            )
            raw_hash = normalized.get("raw_hash", "")
            content_hash = normalized.get("content_hash", "")
            sim_text = f"{normalized.get('title','')} {normalized.get('content_preview','')}"
            sim_fp = simhash_store.fingerprint(sim_text)

            if (
                dedup_store.is_seen(url_hash)
                or (raw_hash and dedup_store.is_seen(raw_hash))
                or (content_hash and dedup_store.is_seen(content_hash))
                or simhash_store.is_similar(sim_fp, max_distance=5)
            ):
                stats["duplicates"] += 1
                continue

            # ── Keyword pre-filter: discard obvious noise immediately ──
            if not keyword_passes(normalized):
                stats["keyword_filtered"] += 1
                dedup_store.add(url_hash)  # mark as seen so we don't re-fetch next time
                if raw_hash:
                    dedup_store.add(raw_hash)
                if content_hash:
                    dedup_store.add(content_hash)
                simhash_store.add(sim_fp)
                continue

            normalized = normalize_article_entities(normalized)
            article_id = normalized.get("raw_hash") or str(uuid.uuid4())[:16]
            normalized["id"] = article_id
            normalized["url_hash"] = url_hash
            normalized["simhash_fp"] = sim_fp
            
            # Turn1 payload için
            normalized["text"] = f"{normalized.get('title', '')}. {normalized.get('content', '')}"
            
            articles_to_process.append(normalized)
            
        except Exception as e:
            logger.error(f"Normalization error: {e}", exc_info=True)
            stats["errors"] += 1

    logger.info(
        f"Keyword filter: {stats['keyword_filtered']} discarded, {len(articles_to_process)} candidates for Turn 1"
    )

    # 3. Turn 1 — LLM relevance classification (batch). Fallback: keyword-only.
    turn1_results: dict[str, dict] = {}
    try:
        payload = [{"id": a["id"], "text": a.get("text", "")} for a in articles_to_process]
        turn1_results = await run_turn1_batch(payload)
    except Exception as e:
        logger.warning(f"Turn1 batch failed, falling back to keyword gate: {e}")
        turn1_results = {}

    if not turn1_results:
        turn1_results = {
            a["id"]: {"relevant": True, "confidence": 0.75, "signal_hint": "Keyword match"}
            for a in articles_to_process
        }
        logger.info(f"Turn 1 (fallback keyword): {len(turn1_results)} passed")
    else:
        passed = sum(1 for r in turn1_results.values() if r.get("relevant"))
        filtered = len(turn1_results) - passed
        logger.info(f"Turn 1 (LLM): {passed} passed, {filtered} filtered out")

    # 4-6. Turn 2 ve Kayıt
    # Cap: only analyse the first N articles per refresh to protect daily quota
    TURN2_MAX_PER_REFRESH = 10
    turn2_count = 0

    # 4-6. Turn 2 ve Kayıt
    for normalized in articles_to_process:
        article_id = normalized["id"]
        url_hash = normalized["url_hash"]
        
        # Eğer turn1'de hata aldıysa veya batch patladıysa atla (zaten hata yazıldı)
        if article_id not in turn1_results:
            continue
            
        t1_res = turn1_results[article_id]
        
        # Alakasız ise dedup yap ve geç
        if not t1_res.get("relevant"):
            dedup_store.add(url_hash)
            if normalized.get("raw_hash"):
                dedup_store.add(normalized["raw_hash"])
            if normalized.get("content_hash"):
                dedup_store.add(normalized["content_hash"])
            if normalized.get("simhash_fp") is not None:
                simhash_store.add(normalized["simhash_fp"])
            continue
            
        # Alakalı -> Turn 2'ye yolla
        try:
            # Enforce per-refresh cap to protect daily quota
            if turn2_count >= TURN2_MAX_PER_REFRESH:
                dedup_store.add(url_hash)  # mark seen so it's skipped next refresh too
                if normalized.get("raw_hash"):
                    dedup_store.add(normalized["raw_hash"])
                if normalized.get("content_hash"):
                    dedup_store.add(normalized["content_hash"])
                if normalized.get("simhash_fp") is not None:
                    simhash_store.add(normalized["simhash_fp"])
                continue

            signal_hint = t1_res.get("signal_hint", "Endüstriyel relokasyon sinyali")
            # Throttle: 8s gap = max 7.5 RPM, safely under 10 RPM free tier limit
            if turn2_count > 0:
                await asyncio.sleep(8)
            turn2_count += 1
            logger.info(f"Turn 2 [{turn2_count}/{TURN2_MAX_PER_REFRESH}]: {normalized.get('title', '')[:60]}")
            turn2 = await process_article_turn2(normalized, signal_hint)
            
            if not turn2 or turn2.get("_failed"):
                article = {
                    **normalized,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "analysis_status": "failed",
                    "error": turn2.get("_failed") if turn2 else "turn2_failed",
                }
                await articles_store.save(article)
                dedup_store.add(url_hash)
                if normalized.get("raw_hash"):
                    dedup_store.add(normalized["raw_hash"])
                if normalized.get("content_hash"):
                    dedup_store.add(normalized["content_hash"])
                if normalized.get("simhash_fp") is not None:
                    simhash_store.add(normalized["simhash_fp"])
                stats["errors"] += 1
                continue

            # AI sonucunu article'a ekle
            article = {
                **normalized,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "analysis_status": "processed",
                "event_type":         turn2.get("event_type", "other"),
                "summary_tr":         turn2.get("summary_tr"),
                "company":            turn2.get("company") or normalized.get("company"),
                "from_location":      turn2.get("from_location") or normalized.get("from_location"),
                "to_location":        turn2.get("to_location") or normalized.get("to_location"),
                "sector":             turn2.get("sector"),
                "subsector":          turn2.get("subsector"),
                "timeline":           turn2.get("timeline"),
                "capex_eur":          turn2.get("capex_eur"),
                "jobs_impact":        turn2.get("jobs_impact"),
                "line_type":          turn2.get("line_type"),
                "equipment_keywords": turn2.get("equipment_keywords", []),
                "signal_type":        turn2.get("signal_type", "neutral"),
                "ai_confidence":      t1_res.get("confidence", turn2.get("confidence", 0.5)),
                "reasoning":          turn2.get("reasoning"),
                "assumptions":        turn2.get("assumptions", []),
            }

            # Skor hesapla
            score_result = calculate_bios_score(article, graph_delta=0.0)
            trail = build_audit_trail(article, score_result)
            score_result["audit_trail"] = trail
            article["bios_fit"] = score_result

            # Kaydet
            await articles_store.save(article)
            dedup_store.add(url_hash)
            if normalized.get("raw_hash"):
                dedup_store.add(normalized["raw_hash"])
            if normalized.get("content_hash"):
                dedup_store.add(normalized["content_hash"])
            if normalized.get("simhash_fp") is not None:
                simhash_store.add(normalized["simhash_fp"])

            # Anomali geçmişine ekle
            anomaly_engine.record(
                article.get("company"),
                article.get("to_location") or article.get("from_location"),
                article_id,
                article.get("published_at")
            )

            new_articles.append(article)
            stats["new"] += 1
            logger.info(f"Processed: [{score_result['label']}] {article['title'][:60]}")

            # RAG için otomatik sorular üret
            _generate_auto_questions(article)

        except Exception as e:
            logger.error(f"Pipeline error for article: {e}", exc_info=True)
            stats["errors"] += 1

    # 7. Graf güncelle (tüm haberler üzerinde)
    if new_articles:
        try:
            all_arts = articles_store.list_all()
            processed = [a for a in all_arts if a.get("analysis_status") == "processed"]
            edges = graph_engine.build_graph_edges(processed)
            deltas = graph_engine.propagate_scores(processed, edges)

            # Skor güncelle — yalnızca graph delta değişenler veya synapse skoru eklenenler
            for article in processed:
                aid = article.get("id")
                delta = deltas.get(aid, 0.0)
                syn_score, syn_breakdown = graph_engine.calculate_synapse_score(aid, edges, processed)
                
                needs_update = False
                
                if article.get("bios_fit"):
                    old_delta = article["bios_fit"].get("adjustments", {}).get("graph_delta", 0)
                    if abs(delta - old_delta) > 0.1:
                        needs_update = True
                        
                if article.get("synapse_score") != syn_score or not article.get("synapse_breakdown"):
                    needs_update = True
                    
                if needs_update and article.get("bios_fit"):
                    new_score = calculate_bios_score(article, graph_delta=delta)
                    new_score["audit_trail"] = build_audit_trail(article, new_score)
                    article["bios_fit"] = new_score
                    article["synapse_score"] = syn_score
                    article["synapse_breakdown"] = syn_breakdown
                    # Komşuları da ekle
                    article["graph_neighbors"] = graph_engine.get_neighbors(aid, processed, edges)
                    await articles_store.save(article)

            # Extra Layers: Create Multi-layer Graph Data
            multi_nodes = []
            multi_edges = list(edges)
            seen_sectors = set()
            seen_companies = set()
            
            for a in processed:
                # Base node
                multi_nodes.append({"id": a["id"], "group": "article", "company": a.get("company"), "location": a.get("to_location")})
                
                # Sector Layer
                sec = a.get("sector")
                if sec and sec != "other":
                    sec_id = f"sector_{sec.lower().replace(' ', '_')}"
                    if sec_id not in seen_sectors:
                        multi_nodes.append({"id": sec_id, "group": "sector", "label": sec})
                        seen_sectors.add(sec_id)
                    multi_edges.append({"source": a["id"], "target": sec_id, "relationship": "belongs_to_sector"})

                # Company Layer
                comp = a.get("company")
                if comp and comp.lower() != "unknown":
                    comp_id = f"comp_{comp.lower().replace(' ', '_')}"
                    if comp_id not in seen_companies:
                        multi_nodes.append({"id": comp_id, "group": "company", "label": comp})
                        seen_companies.add(comp_id)
                    multi_edges.append({"source": a["id"], "target": comp_id, "relationship": "mentions_company"})

            graph_engine.save(multi_nodes, multi_edges)
            logger.info(f"Graph updated with multi-layers: {len(multi_edges)} edges")
        except Exception as e:
            logger.error(f"Graph engine error: {e}", exc_info=True)

    # 8. Anomali tespiti sonuçlarını makale flaglerine yaz
    try:
        anomalies = anomaly_engine.detect()
        anomaly_article_ids = set()
        anomaly_map = {}
        for anom in anomalies:
            for aid in anom.get("related_article_ids", []):
                anomaly_article_ids.add(aid)
                anomaly_map[aid] = anom["multiplier"]

        for article in new_articles:
            aid = article.get("id")
            if aid in anomaly_article_ids:
                article["has_anomaly"] = True
                article["anomaly_multiplier"] = anomaly_map.get(aid)
                await articles_store.save(article)
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}", exc_info=True)

    duration = (datetime.now(timezone.utc) - start).total_seconds()
    stats["duration_seconds"] = round(duration, 1)

    # Yüksek fırsat sayısı
    stats["high_opportunity_count"] = sum(
        1 for a in new_articles
        if (a.get("bios_fit") or {}).get("score_final", 0) >= 80
    )

    logger.info(f"Refresh done: {stats}")
    return stats
