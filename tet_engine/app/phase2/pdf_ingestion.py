from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class ParsedChunk:
    chunk_index: int
    content: str


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[ParsedChunk]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[ParsedChunk] = []
    start = 0
    idx = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        part = normalized[start:end]
        chunks.append(ParsedChunk(chunk_index=idx, content=part))
        idx += 1
        start += max(1, chunk_size - overlap)
    return chunks


def keyword_retrieve(chunks: list[ParsedChunk], query: str, top_k: int = 5) -> list[ParsedChunk]:
    query_tokens = {token.lower() for token in query.split() if token.strip()}
    scored: list[tuple[int, ParsedChunk]] = []

    for chunk in chunks:
        chunk_tokens = set(chunk.content.lower().split())
        overlap = len(query_tokens.intersection(chunk_tokens))
        scored.append((overlap, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0] or chunks[:top_k]
