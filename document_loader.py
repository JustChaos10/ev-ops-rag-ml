"""Utilities for loading uploaded documents into the RAG pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

TEXT_EXTENSIONS = {".txt", ".md", ".json"}


def load_documents(upload_dir: Path) -> List[dict]:
    """Return document dicts for all supported files inside the upload directory."""
    if not upload_dir.exists():
        return []

    documents: List[dict] = []
    for path in sorted(upload_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in TEXT_EXTENSIONS:
            continue

        try:
            # Treat JSON as raw text for simplicity; users can paste summaries or extracts.
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        rel_id = path.relative_to(upload_dir).as_posix()
        documents.append(
            {
                "id": f"upload::{rel_id}",
                "text": text,
                "tags": ["upload"],
                "source_path": str(path),
            }
        )
    return documents


def describe_sources(documents: Iterable[dict]) -> List[str]:
    """Produce a small summary list of source identifiers for UI display."""
    return [doc.get("id", "unknown") for doc in documents]
