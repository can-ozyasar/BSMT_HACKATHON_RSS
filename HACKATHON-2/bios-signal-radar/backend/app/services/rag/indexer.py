import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_WORD_RE = re.compile(r"[\\wğüşöçıİĞÜŞÖÇ]+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text or "")]


def _split_markdown(md: str) -> list[tuple[str, str]]:
    """
    Returns list of (section_title, section_text) chunks.
    Chunking is heading-based to keep citations meaningful.
    """
    lines = (md or "").splitlines()
    chunks: list[tuple[str, list[str]]] = []
    current_title = "Giriş"
    current_lines: list[str] = []

    def flush():
        nonlocal current_lines, current_title
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append((current_title, text.splitlines()))
        current_lines = []

    for line in lines:
        m = re.match(r"^(#{1,3})\\s+(.+?)\\s*$", line)
        if m:
            flush()
            current_title = m.group(2).strip()
            continue
        current_lines.append(line)

    flush()

    # Limit chunk size roughly (prevent huge prompts)
    out: list[tuple[str, str]] = []
    for title, section_lines in chunks:
        buf: list[str] = []
        for ln in section_lines:
            buf.append(ln)
            if len(buf) >= 80:
                out.append((title, "\n".join(buf).strip()))
                buf = []
        if buf:
            out.append((title, "\n".join(buf).strip()))
    return out


@dataclass(frozen=True)
class RagChunk:
    id: str
    file: str
    title: str
    text: str
    tokens: list[str]


class RagIndex:
    def __init__(self, chunks: list[RagChunk], meta: dict):
        self.chunks = chunks
        self.meta = meta

    def to_json(self) -> dict:
        return {
            "meta": self.meta,
            "chunks": [
                {
                    "id": c.id,
                    "file": c.file,
                    "title": c.title,
                    "text": c.text,
                    "tokens": c.tokens,
                }
                for c in self.chunks
            ],
        }

    @staticmethod
    def from_json(data: dict) -> "RagIndex":
        chunks = [
            RagChunk(
                id=c["id"],
                file=c["file"],
                title=c["title"],
                text=c["text"],
                tokens=c.get("tokens") or _tokenize(c.get("text") or ""),
            )
            for c in (data.get("chunks") or [])
        ]
        return RagIndex(chunks=chunks, meta=data.get("meta") or {})


def _iter_md_files(base_dirs: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for d in base_dirs:
        if not d.exists():
            continue
        files.extend(sorted(p for p in d.rglob("*.md") if p.is_file()))
    return files


def build_index(md_dirs: list[Path]) -> RagIndex:
    files = _iter_md_files(md_dirs)
    chunks: list[RagChunk] = []
    for path in files:
        rel = path.as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, (title, chunk_text) in enumerate(_split_markdown(text)):
            cid = f"{rel}:::{i}"
            chunks.append(
                RagChunk(
                    id=cid,
                    file=rel,
                    title=title,
                    text=chunk_text.strip(),
                    tokens=_tokenize(chunk_text),
                )
            )

    meta = {
        "file_count": len(files),
        "chunk_count": len(chunks),
        "files": [p.as_posix() for p in files],
    }
    return RagIndex(chunks=chunks, meta=meta)


def load_or_build(index_path: Path, md_dirs: list[Path]) -> RagIndex:
    """
    Very simple cache: rebuild when file list or mtimes change.
    """
    files = _iter_md_files(md_dirs)
    signature = {p.as_posix(): int(p.stat().st_mtime) for p in files}

    if index_path.exists():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            meta = data.get("meta") or {}
            if meta.get("signature") == signature:
                return RagIndex.from_json(data)
        except Exception:
            pass

    idx = build_index(md_dirs)
    idx.meta["signature"] = signature
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(idx.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")
    return idx

