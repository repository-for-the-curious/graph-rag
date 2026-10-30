"""Heading-aware Markdown chunking.

Sections are cut at headings (ignoring '#' inside code fences), then long sections
are packed paragraph by paragraph up to `size` characters, with `overlap`
characters carried over so an instruction is not cut from its context.
"""

from __future__ import annotations

import hashlib

from kh_graphrag.models import Chunk, Note


def _sections(body: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = [("", [])]
    stack: list[tuple[int, str]] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line[level:].strip()
            if 1 <= level <= 6 and title and line[level : level + 1] == " ":
                stack = [(lv, t) for lv, t in stack if lv < level] + [(level, title)]
                sections.append((" > ".join(t for _, t in stack), [line]))
                continue
        sections[-1][1].append(line)
    return [(h, "\n".join(lines).strip()) for h, lines in sections if "\n".join(lines).strip()]


def _pack(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]
    parts: list[str] = []
    for para in text.split("\n\n"):
        while len(para) > size:  # a single huge paragraph (e.g. a long code block)
            parts.append(para[:size])
            para = para[size - overlap :]
        parts.append(para)
    chunks: list[str] = []
    current = ""
    for para in parts:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= size:
            current = candidate
            continue
        if current:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}" if tail else para
            if len(current) > size:
                current = para
        else:
            current = para
    if current:
        chunks.append(current)
    return chunks


def _merge_small(sections: list[tuple[str, str]], size: int) -> list[tuple[str, str]]:
    """Join consecutive short sections (headings with a few lines) up to `size`."""
    merged: list[tuple[str, str]] = []
    for heading, text in sections:
        if merged and len(merged[-1][1]) + len(text) + 2 <= size:
            merged[-1] = (merged[-1][0] or heading, f"{merged[-1][1]}\n\n{text}")
        else:
            merged.append((heading, text))
    return merged


def chunk_note(note: Note, size: int = 1200, overlap: int = 150) -> list[Chunk]:
    chunks: list[Chunk] = []
    for heading, text in _merge_small(_sections(note.body), size):
        for piece in _pack(text, size, overlap):
            if len(piece.strip()) < 40:
                continue
            ordinal = len(chunks)
            digest = hashlib.sha1(f"{note.path}#{ordinal}".encode()).hexdigest()[:16]
            chunks.append(
                Chunk(id=digest, note_path=note.path, ord=ordinal, heading=heading, text=piece)
            )
    return chunks


def chunk_notes(notes: list[Note], size: int = 1200, overlap: int = 150) -> list[Chunk]:
    return [c for n in notes for c in chunk_note(n, size, overlap)]
