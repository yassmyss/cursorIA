"""Small, inspectable retrieval layer; no vector database required."""
from dataclasses import dataclass
from pathlib import Path
import math
import re
import unicodedata


@dataclass(frozen=True)
class Chunk:
    id: str
    title: str
    section: str
    text: str
    source: str
    kind: str
    reviewed: str


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


def load_chunks(folder: Path, size: int = 900, overlap: int = 120) -> list[Chunk]:
    if size < 1 or not 0 <= overlap < size:
        raise ValueError('Tamaño y solapamiento de fragmentos no válidos.')
    chunks = []
    for path in sorted(folder.glob('*.md')):
        raw = path.read_text(encoding='utf-8')
        if not raw.startswith('---\n') or '\n---\n' not in raw[4:]:
            raise ValueError(f'{path.name}: falta la cabecera de metadatos.')
        header, body = raw[4:].split('\n---\n', 1)
        meta = dict(line.split(': ', 1) for line in header.splitlines() if ': ' in line)
        if any(not meta.get(key) for key in ('title', 'source', 'kind', 'reviewed')):
            raise ValueError(f'{path.name}: metadatos incompletos.')
        section = meta['title']
        parts = re.split(r'(?m)^## (.+)\n', body)
        sections = [(section, parts[0])]
        sections.extend(zip(parts[1::2], parts[2::2]))
        number = 0
        for section, content in sections:
            content = content.strip()
            for start in range(0, len(content), size - overlap):
                piece = content[start:start + size].strip()
                if piece:
                    number += 1
                    chunks.append(Chunk(f'{path.stem}:{number}', meta['title'], section,
                                        piece, meta['source'], meta['kind'], meta['reviewed']))
                if start + size >= len(content):
                    break
    if not chunks:
        raise ValueError('No hay documentos con contenido en la carpeta.')
    return chunks


def tokens(text: str) -> set[str]:
    normalized = ''.join(c for c in unicodedata.normalize('NFD', text.lower())
                         if unicodedata.category(c) != 'Mn')
    stop = set('de la el los las un una en a y que como para con del es se por mi al'.split())
    return set(re.findall(r'[a-z0-9_]+', normalized)) - stop


def lexical_search(chunks: list[Chunk], question: str, k: int = 3) -> list[Hit]:
    """Transparent demo baseline: word overlap, NOT semantic embeddings."""
    query = tokens(question)
    hits = []
    for chunk in chunks:
        words = tokens(chunk.title + ' ' + chunk.section + ' ' + chunk.text)
        score = len(query & words) / max(len(query), 1)
        if score > 0:
            hits.append(Hit(chunk, score))
    return sorted(hits, key=lambda h: (-h.score, h.chunk.id))[:k]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or len(a) != len(b):
        raise ValueError('Dimensiones de embeddings incompatibles.')
    if not all(math.isfinite(x) for x in a + b):
        raise ValueError('Embedding con valores no finitos.')
    denominator = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / denominator if denominator else 0.0


def semantic_search(chunks: list[Chunk], vectors: list[list[float]], query: list[float],
                    k: int = 3, threshold: float = 0.3) -> list[Hit]:
    if len(chunks) != len(vectors):
        raise ValueError('El índice no corresponde a los documentos.')
    hits = [Hit(chunk, cosine(vector, query)) for chunk, vector in zip(chunks, vectors)]
    return sorted((h for h in hits if h.score >= threshold),
                  key=lambda h: (-h.score, h.chunk.id))[:k]
