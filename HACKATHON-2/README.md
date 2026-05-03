# BIOS Signal Radar

Avrupa endüstriyel haberlerini RSS üzerinden toplayıp (dedup + temizleme), yerel LLM (Ollama/Llama3) ile 2 turlu analiz ederek “sinyal” ve “BIOS-Fit” skoru üreten demo ürün.

## Klasörler

- `bios-signal-radar/backend` — FastAPI API
- `bios-signal-radar/frontend` — React + Vite UI
- `docs/` — proje ve teknik dokümantasyon (giriş: `docs/00_INDEX.md`)

## Hızlı Başlangıç (Local)

### 1) Ollama

- Ollama’yı kurup çalıştırın ve bir model çekin (ör. `llama3`).
- Varsayılan backend ayarları: `OLLAMA_BASE_URL=http://localhost:11434`, `OLLAMA_MODEL=llama3`.

### 2) Backend (FastAPI)

```bash
cd bios-signal-radar/backend
cp .env.example .env   # varsa ayarları düzenleyin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

API: `http://localhost:8000` (varsayılan)

### 3) Frontend (React)

```bash
cd bios-signal-radar/frontend
npm install
npm run dev
```

UI: `http://localhost:5173`

## Test (backend)

```bash
cd bios-signal-radar/backend
python3 -m unittest -q
```
