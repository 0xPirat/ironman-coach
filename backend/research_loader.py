"""Small local retrieval layer for the bundled coaching research.

The full research corpus remains on disk. For each coach request we select a
compact set of relevant sections so the model receives useful evidence without
overflowing its context with 1.6 MB of transcripts.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

from .paths import resource_root

_WORD_RE = re.compile(r"[a-zA-ZäöüÄÖÜß0-9]{3,}")
_STOP = {
    "aber", "auch", "dass", "deine", "deinem", "deinen", "einer", "eines",
    "eine", "einen", "für", "oder", "soll", "über", "und", "vom", "was",
    "wenn", "wie", "wird", "with", "from", "that", "this", "the", "you",
}


def research_dir() -> Path:
    override = Path(p) if (p := __import__("os").environ.get("COACH_RESEARCH_DIR")) else None
    return override or (resource_root() / "research")


def _terms(text: str) -> set[str]:
    return {w.casefold() for w in _WORD_RE.findall(text) if w.casefold() not in _STOP}


@functools.lru_cache(maxsize=1)
def _sections() -> tuple[tuple[str, str, frozenset[str]], ...]:
    root = research_dir()
    if not root.exists():
        return ()

    sections: list[tuple[str, str, frozenset[str]]] = []
    # Curated synthesis documents are the coaching source of truth. Raw video
    # transcripts remain shipped for traceability but are not injected verbatim.
    files = sorted(
        p for p in root.rglob("*.md")
        if "youtube-transcripts" not in p.parts and not p.name.startswith(".")
    )
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(root).as_posix()
        chunks = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) < 120:
                continue
            # Keep coherent sections while protecting prompt size.
            for start in range(0, len(chunk), 3600):
                excerpt = chunk[start:start + 4000].strip()
                if len(excerpt) >= 120:
                    sections.append((relative, excerpt, frozenset(_terms(excerpt))))
    return tuple(sections)


def retrieve_research(query: str, *, max_chars: int = 14_000, max_sections: int = 6) -> str:
    """Return the most relevant evidence sections for ``query``."""
    sections = _sections()
    if not sections:
        return ""

    query_terms = _terms(query)
    ranked: list[tuple[float, str, str]] = []
    for source, excerpt, terms in sections:
        overlap = len(query_terms & terms)
        # The main methodology is a useful baseline even for short prompts.
        baseline = 1.25 if source == "ironman-training-methodology.md" else 0.0
        title = excerpt.splitlines()[0].casefold()
        title_overlap = sum(2.5 for term in query_terms if term in title)
        score = baseline + overlap + title_overlap
        if score > 0:
            ranked.append((score, source, excerpt))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    output: list[str] = []
    used = 0
    for _, source, excerpt in ranked[:max_sections]:
        block = f"[Quelle: research/{source}]\n{excerpt}"
        if used + len(block) > max_chars:
            remaining = max_chars - used
            if remaining > 500:
                output.append(block[:remaining].rsplit("\n", 1)[0])
            break
        output.append(block)
        used += len(block)
    return "\n\n---\n\n".join(output)
