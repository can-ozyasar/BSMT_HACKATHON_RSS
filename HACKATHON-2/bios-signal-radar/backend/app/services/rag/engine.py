import math
import re
from dataclasses import dataclass

from app.services.ai_processor import call_ollama

_WORD_RE = re.compile(r"[\wğüşöçıİĞÜŞÖÇ]+", re.UNICODE)


def _tokenize(text: str) -> list:
    return [t.lower() for t in _WORD_RE.findall(text or "")]


@dataclass(frozen=True)
class RagHit:
    score: float
    file: str
    title: str
    text: str


def _article_to_text(a: dict) -> str:
    et_map = {
        "relocation": "Taşınma", "closure": "Kapanış", "expansion": "Genişleme",
        "new_plant": "Yeni Tesis", "tender": "İhale", "other": "Diğer",
    }
    parts = []
    if a.get("title"):
        parts.append(f"Başlık: {a['title']}")
    if a.get("company"):
        parts.append(f"Şirket: {a['company']}")
    if a.get("event_type"):
        parts.append(f"Olay: {et_map.get(a['event_type'], a['event_type'])}")
    if a.get("sector"):
        parts.append(f"Sektör: {a['sector']}")
    if a.get("from_location"):
        parts.append(f"Nereden: {a['from_location']}")
    if a.get("to_location"):
        parts.append(f"Nereye: {a['to_location']}")
    bios = (a.get("bios_fit") or {}).get("score_final", 0)
    if bios:
        parts.append(f"BIOS: {bios}")
    if a.get("summary_tr"):
        parts.append(f"Özet: {a['summary_tr'][:200]}")
    date = a.get("published_at") or a.get("fetched_at") or ""
    if date:
        parts.append(f"Tarih: {date[:10]}")
    return " | ".join(parts)


def _score_article(a: dict, q_tokens: set) -> float:
    text = _article_to_text(a)
    tokens = [t.lower() for t in _WORD_RE.findall(text)]
    overlap = sum(1 for t in tokens if t in q_tokens)
    if overlap == 0:
        return 0.0
    bios_bonus = (a.get("bios_fit") or {}).get("score_final", 0) / 1000.0
    return overlap / math.sqrt(max(20, len(tokens))) + bios_bonus


class RagEngine:
    def _retrieve(self, q_tokens: set, k: int = 5) -> list[RagHit]:
        from app.storage.articles_store import articles_store
        processed = [
            a for a in articles_store.list_all()
            if a.get("analysis_status") == "processed"
        ]
        scored = sorted(
            [(s, a) for a in processed if (s := _score_article(a, q_tokens)) > 0],
            key=lambda x: x[0],
            reverse=True,
        )
        return [
            RagHit(score=s, file="haberler", title=a.get("company") or a.get("title") or "Haber", text=_article_to_text(a))
            for s, a in scored[:k]
        ]

    def retrieve(self, query: str, k: int = 5) -> list[RagHit]:
        q_tokens = set(_tokenize(query))
        return self._retrieve(q_tokens, k) if q_tokens else []

    async def ask(self, question: str, mode: str = "genel") -> dict:
        q_tokens = set(_tokenize(question))
        hits = self._retrieve(q_tokens, k=5)

        if not hits:
            return {
                "answer_tr": "Bu konuyla ilgili veritabanında haber bulunamadı. 'Tümünü Yenile' ile haberleri güncelleyin.",
                "sources": [],
            }

        context = "\n".join(f"{i}. {h.text}" for i, h in enumerate(hits, 1))

        system = (
            "Sen endüstriyel haber asistanısın. "
            "Sadece verilen haberlere dayan. "
            "Türkçe, en fazla 2-3 cümle yaz. "
            "Bilgi yoksa 'Bu konuda veri yok.' de."
        )
        user = f"Soru: {question}\n\nHaberler:\n{context}\n\nYanıt:"

        text = await call_ollama(system=system, user=user, max_tokens=250)
        answer = (text or "").strip() or "Yanıt üretilemedi. Ollama servisini kontrol edin."

        return {"answer_tr": answer, "sources": [{"title": h.title} for h in hits[:3]]}


rag_engine = RagEngine()
