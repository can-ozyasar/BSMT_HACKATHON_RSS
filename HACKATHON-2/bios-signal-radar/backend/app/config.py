from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Ollama / Local LLM ────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ── Server ────────────────────────────────────────────────────────────────
    port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # ── App flags ─────────────────────────────────────────────────────────────
    demo_mode: bool = False

    # ── Scoring thresholds ────────────────────────────────────────────────────
    score_high_threshold: int = 80
    score_watch_threshold: int = 65
    score_partner_threshold: int = 50

    # ── Anomaly detection ─────────────────────────────────────────────────────
    anomaly_window_hours: int = 6
    anomaly_baseline_days: int = 7
    anomaly_spike_threshold: float = 4.0

    # ── Scheduler ─────────────────────────────────────────────────────────────
    enable_scheduler: bool = False
    refresh_interval_minutes: int = 30

    # ── Data directory ────────────────────────────────────────────────────────
    data_dir: str = "data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
