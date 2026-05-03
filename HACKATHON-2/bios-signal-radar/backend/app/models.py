from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal
from datetime import datetime


# ─── RSS Kaynak ─────────────────────────────────────────────────────────────

class RSSSource(BaseModel):
    id: str
    url: str
    name: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    status: Literal["active", "error", "pending"] = "active"
    last_fetched_at: Optional[str] = None
    error_message: Optional[str] = None
    added_at: str
    article_count: int = 0


class RSSSourceCreate(BaseModel):
    url: str
    name: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


# ─── AI Pipeline ─────────────────────────────────────────────────────────────

class Turn1Result(BaseModel):
    relevant: bool
    confidence: float = Field(ge=0, le=1)
    signal_hint: str


class Turn2Result(BaseModel):
    event_type: Literal["relocation", "closure", "expansion", "new_plant", "tender", "other"]
    summary_tr: str = Field(min_length=5)
    company: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None
    timeline: Optional[str] = None
    capex_eur: Optional[float] = None
    jobs_impact: Optional[int] = None
    line_type: Optional[str] = None
    equipment_keywords: list[str] = Field(default_factory=list)
    signal_type: Literal["positive", "negative", "neutral"] = "neutral"
    confidence: float = Field(ge=0, le=1, default=0.5)
    reasoning: str = ""
    assumptions: list[str] = Field(default_factory=list)


# ─── Haber (Article) ─────────────────────────────────────────────────────────

class BiosScore(BaseModel):
    score: int = Field(ge=0, le=100)
    raw_score: float
    confidence: float
    components: dict  # E, A, G, T, C
    adjustments: dict
    label: str
    color: Literal["green", "blue", "yellow", "gray"]
    action: str
    audit_trail: list[dict] = Field(default_factory=list)
    graph_delta: float = 0.0
    score_final: int = 0


class Article(BaseModel):
    id: str
    title: str
    original_url: str
    source_id: str
    source_name: str
    source_url: str
    published_at: Optional[str] = None
    fetched_at: str
    language: Optional[str] = None
    raw_hash: str
    content_preview: Optional[str] = None

    # AI Analysis
    analysis_status: Literal["pending", "processed", "failed", "irrelevant"] = "pending"
    event_type: Optional[str] = None
    summary_tr: Optional[str] = None
    company: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None
    timeline: Optional[str] = None
    capex_eur: Optional[float] = None
    jobs_impact: Optional[int] = None
    line_type: Optional[str] = None
    equipment_keywords: list[str] = Field(default_factory=list)
    signal_type: Optional[str] = "neutral"
    ai_confidence: float = 0.0
    reasoning: Optional[str] = None
    assumptions: list[str] = Field(default_factory=list)

    # Scoring
    bios_fit: Optional[BiosScore] = None

    # Graph
    graph_neighbors: list[dict] = Field(default_factory=list)

    # Anomaly
    has_anomaly: bool = False
    anomaly_multiplier: Optional[float] = None


# ─── Anomali ─────────────────────────────────────────────────────────────────

class AnomalySignal(BaseModel):
    entity: str
    entity_type: Literal["company", "location"]
    article_count_recent: int
    article_count_baseline: float
    multiplier: float
    threshold: float = 4.0
    detected_at: str
    related_article_ids: list[str] = Field(default_factory=list)


# ─── Refresh ─────────────────────────────────────────────────────────────────

class RefreshResponse(BaseModel):
    fetched: int
    new: int
    duplicates: int
    errors: int
    duration_seconds: float
    high_opportunity_count: int = 0


# ─── Stats ────────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_articles: int
    high_opportunity: int
    watchlist: int
    conditional: int
    low_relevance: int
    total_sources: int
    active_anomalies: int
    last_refresh: Optional[str] = None
