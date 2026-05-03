"""Dedup storage — URL/content hashes + SimHash fingerprints."""
import json
import hashlib
from pathlib import Path

from simhash import Simhash

DATA_DIR = Path("data")
HASHES_FILE = DATA_DIR / "seen_hashes.json"
SIMHASH_FILE = DATA_DIR / "seen_simhashes.json"


class DedupStore:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        if not HASHES_FILE.exists():
            HASHES_FILE.write_text("[]", encoding="utf-8")
        self._cache: set[str] = set(self._load())

    def _load(self) -> list[str]:
        try:
            return json.loads(HASHES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self):
        HASHES_FILE.write_text(
            json.dumps(list(self._cache), ensure_ascii=False),
            encoding="utf-8"
        )

    def is_seen(self, hash_val: str) -> bool:
        return hash_val in self._cache

    def add(self, hash_val: str):
        self._cache.add(hash_val)
        self._save()

    @staticmethod
    def make_hash(url: str, title: str) -> str:
        content = f"{url}|{title}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class GraphStore:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self._file = DATA_DIR / "graph.json"

    def read(self) -> dict:
        if not self._file.exists():
            return {"nodes": [], "edges": []}
        try:
            return json.loads(self._file.read_text(encoding="utf-8"))
        except Exception:
            return {"nodes": [], "edges": []}

    def write(self, graph: dict):
        self._file.write_text(
            json.dumps(graph, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get_neighbors(self, article_id: str) -> list[dict]:
        graph = self.read()
        neighbors = []
        for edge in graph.get("edges", []):
            if edge["source"] == article_id:
                neighbors.append({"id": edge["target"], **edge})
            elif edge["target"] == article_id:
                neighbors.append({"id": edge["source"], **edge})
        return neighbors


dedup_store = DedupStore()
graph_store = GraphStore()


class SimhashDedupStore:
    """
    Simple SimHash store (O(n) distance check).
    Intended for hackathon-scale volumes (tens/hundreds of articles).
    """

    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        if not SIMHASH_FILE.exists():
            SIMHASH_FILE.write_text("[]", encoding="utf-8")
        self._values: list[int] = self._load()

    def _load(self) -> list[int]:
        try:
            raw = json.loads(SIMHASH_FILE.read_text(encoding="utf-8"))
            return [int(x) for x in raw]
        except Exception:
            return []

    def _save(self):
        SIMHASH_FILE.write_text(
            json.dumps(self._values, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _hamming(a: int, b: int) -> int:
        return (a ^ b).bit_count()

    @staticmethod
    def fingerprint(text: str) -> int:
        return int(Simhash(text or "").value)

    def is_similar(self, fp: int, max_distance: int = 5) -> bool:
        for existing in self._values:
            if self._hamming(existing, fp) <= max_distance:
                return True
        return False

    def add(self, fp: int):
        self._values.append(int(fp))
        # Keep file from growing unbounded in demo mode.
        if len(self._values) > 5000:
            self._values = self._values[-5000:]
        self._save()


simhash_store = SimhashDedupStore()
