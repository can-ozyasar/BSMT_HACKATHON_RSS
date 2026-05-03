# BIOS Signal Radar

**Avrupa Endüstriyel Haber Tarama Ajanı** — RSS tabanlı, yapay zekâ destekli, gerçek zamanlı haber analiz sistemi.

---

## Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) + `llama3` modeli (yerel LLM)

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # OLLAMA_BASE_URL ve MODEL ayarlayın
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173 adresinden erişin
```

---

## Test RSS Kaynakları

Sistemi test etmek için aşağıdaki RSS bağlantılarını ekleyebilirsiniz:

| Kaynak | URL |
|--------|-----|
| Reuters Business | `https://feeds.reuters.com/reuters/businessNews` |
| Manufacturing.net | `https://www.manufacturing.net/rss` |
| IndustryWeek | `https://www.industryweek.com/rss` |
| Handelsblatt | `https://www.handelsblatt.com/contentexport/feed/schlagzeilen` |
| Just-Auto | `https://www.just-auto.com/rss` |

---

## Yapay Zekâ Prompt'ları

### Tur 1 — Ön Sınıflandırma (Relevance Filter)

Sistem prompt:
```
You are an industrial news classifier for BIOS Signal Radar.

Classify whether a news article belongs to one of these RELEVANT signal categories:
1. FACTORY & PRODUCTION MOVEMENT - factory relocation, closure, new plant, capacity change
2. WORKFORCE & RESTRUCTURING - mass layoffs (500+ people), workforce reduction, consolidation
3. STRATEGIC CORPORATE NEWS - major M&A, bankruptcy, outsourcing decisions, supply chain restructuring
4. INVESTMENT & TENDER - major CapEx announcements, industrial equipment tenders, government-backed factory investments
5. SECTOR DISRUPTION - crisis in automotive, steel, chemical, textile, electronics

IRRELEVANT: sports, culture, food, travel, pure stock market commentary, central bank rate decisions without industrial impact.
```

JSON çıktı şeması (Tur 1):
```json
{
  "relevant": true,
  "confidence": 0.92,
  "signal_hint": "Factory relocation signal detected"
}
```

### Tur 2 — Derin Analiz ve Çıkarım

Sistem prompt:
```
Sen bir endüstriyel haber analistsin. Aşağıdaki haber metninden olay tipini,
şirket adını, lokasyonları ve sektörü çıkar. Haberin Avrupa'daki bir fabrika
taşıması, kapanışı, genişlemesi veya yeni yatırımı ile ilgili olup olmadığına
göre 0–100 arası alaka skoru ver. SADECE JSON döndür, başka hiçbir şey yazma.
Bilmediğin alanları null bırak. Özeti Türkçe yaz.

METIN: {{article_text}}
```

JSON çıktı şeması (Tur 2):
```json
{
  "event_type": "relocation | closure | expansion | new_plant | tender | other",
  "summary_tr": "Türkçe 2–4 cümlelik özet",
  "company": "Şirket adı veya null",
  "from_location": "Çıkış lokasyonu veya null",
  "to_location": "Hedef lokasyon veya null",
  "sector": "Sektör veya null",
  "subsector": "Alt sektör veya null",
  "timeline": "Zaman bilgisi veya null",
  "capex_eur": null,
  "jobs_impact": null,
  "signal_type": "positive | negative | neutral",
  "confidence": 0.85,
  "reasoning": "Karar gerekçesi",
  "assumptions": []
}
```

### Synapse AI Skoru

```
Sen BIOS Signal Radar için 'Synapse AI' skorlayıcısın.
Amaç: Bu haberi grafik ağındaki bağlamına göre 0-100 arası 'Synapse AI' skoru üretmek.
- Her zaman Türkçe cevap ver.
- Skor 0-100 tam sayı.
- Çıktı SADECE JSON olsun (markdown yok).

JSON Şeması:
{
  "synapse_ai_score": 0,
  "reasoning_tr": "2-4 cümle kısa gerekçe",
  "key_factors": ["madde", "madde"]
}
```

### RAG Asistan

```
Sen BIOS Signal Radar'ın Türkçe konuşan AI asistanısın.
Görevin: Verilen kaynak dökümanlarına dayalı olarak kullanıcının sorularını yanıtlamak.
- Yanıtlarını 3–5 cümle ile sınırla.
- Kaynakta olmayan bilgiler için "Bu konuda kaynağımda yeterli veri yok." de.
- Her zaman Türkçe yanıt ver.
```

---

## BIOS-Fit Skor Formülü

```
Score = 100 × (0.30·E + 0.25·A + 0.20·G + 0.15·T + 0.10·C)
```

| Bileşen | Açıklama | Max Puan |
|---------|----------|----------|
| E — Olay Tipi | relocation=1.0, new_plant=0.9, expansion=0.75 | 30 |
| A — Aktör Netliği | şirket+from+to+sektör dolduğu kadar | 25 |
| G — Coğrafya | Avrupa içi=1.0, komşu=0.5, diğer=0.1 | 20 |
| T — Zaman Penceresi | 0-6 ay=1.0, 6-18 ay=0.7, belirsiz=0.2 | 15 |
| C — Kaynak Güveni | Resmi site=1.0, Reuters/FT=0.85, Sektörel=0.7 | 10 |

> Confidence < 0.40 ise Score × 0.50 uygulanır (ceza).

### Örnek Hesaplama

**Haber:** BMW, Münih'teki üretim hattını Macaristan/Debrecen'e taşıyor (Reuters, 2026 Q1)

| Bileşen | Değer | Puan |
|---------|-------|------|
| E (relocation) | 1.00 | 30.0 |
| A (tüm alanlar dolu) | 1.00 | 25.0 |
| G (Almanya→Macaristan, Avrupa içi) | 1.00 | 20.0 |
| T (2026 Q1, <6 ay) | 1.00 | 15.0 |
| C (Reuters) | 0.85 | 8.5 |
| **Toplam** | | **98.5 → 99** |

---

## Mimari

```
RSS Kaynakları → Collector → Normalizer → Dedup → Turn1 (LLM) → Turn2 (LLM)
                                                                      ↓
                                                              BIOS Scorer
                                                                      ↓
                                                         Graph Engine + Anomaly
                                                                      ↓
                                                              Frontend (React)
```

## Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Frontend | React 19, Vite, TailwindCSS 4, Zustand, Sonner |
| Backend | FastAPI, Python 3.11, Pydantic |
| LLM | Ollama (llama3 / llama3.2) |
| RSS | feedparser |
| Grafik | react-force-graph-2d |
| Veri | JSON dosya tabanlı (SQLite-free) |
