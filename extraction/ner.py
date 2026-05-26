"""
extraction/ner.py
US-202 — NER Pipeline using spaCy

Extracts named entities from text segments using spaCy's
en_core_web_lg model.

Acceptance Criteria:
  - Entities identified with acceptable accuracy
  - Setup NLP pipeline
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Optional

# spaCy entity labels we care about for knowledge graph
RELEVANT_LABELS = {
    "PERSON",    # People, including fictional
    "ORG",       # Companies, agencies, institutions
    "GPE",       # Countries, cities, states
    "LOC",       # Non-GPE locations, mountain ranges, bodies of water
    "DATE",      # Absolute or relative dates or periods
    "MONEY",     # Monetary values
    "PRODUCT",   # Objects, vehicles, foods, etc.
    "EVENT",     # Named hurricanes, battles, wars, sports events
    "WORK_OF_ART",  # Titles of books, songs, etc.
    "LAW",       # Named documents made into laws
    "NORP",      # Nationalities or religious or political groups
    "FAC",       # Buildings, airports, highways, bridges, etc.
    "LANGUAGE",  # Any named language
    "PERCENT",   # Percentage
    "QUANTITY",  # Measurements
    "TIME",      # Times smaller than a day
    "CARDINAL",  # Numerals that do not fall under another type
    "ORDINAL",   # "first", "second", etc.
}


@dataclass
class Entity:
    """
    A named entity extracted from text.
    """
    text: str          # The surface form (e.g., "Elon Musk")
    label: str         # spaCy label (e.g., "PERSON")
    normalized: str    # Lowercased, stripped for deduplication
    start_char: int    # Character offset in source text
    end_char: int      # Character offset in source text
    source: str = ""   # File name this came from

    def __repr__(self) -> str:
        return f"Entity({self.text!r}, {self.label})"

    def __hash__(self):
        return hash((self.normalized, self.label))

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.normalized == other.normalized and self.label == other.label


class NERExtractor:
    """
    US-202: Named Entity Recognition pipeline using spaCy.

    Tries to load en_core_web_lg first (most accurate),
    falls back to en_core_web_sm if not installed.

    Usage:
        ner = NERExtractor()
        entities = ner.extract("Apple was founded by Steve Jobs in Cupertino.")
    """

    def __init__(self, model: str = "en_core_web_lg"):
        self.model_name = model
        self.nlp = self._load_model(model)

    def _load_model(self, model_name: str):
        """Load spaCy model, with fallback guidance."""
        try:
            import spacy
            return spacy.load(model_name)
        except OSError:
            # Try fallback to sm model
            try:
                import spacy
                print(
                    f"⚠️  '{model_name}' not found. Falling back to 'en_core_web_sm'.\n"
                    f"    For better accuracy, run:\n"
                    f"    .venv\\Scripts\\python -m spacy download {model_name}"
                )
                return spacy.load("en_core_web_sm")
            except OSError:
                raise RuntimeError(
                    "No spaCy English model found.\n"
                    "Install one with:\n"
                    "  .venv\\Scripts\\python -m spacy download en_core_web_lg\n"
                    "  (or en_core_web_sm for the lighter version)"
                )
        except ImportError:
            raise ImportError(
                "spaCy not installed. Run:\n"
                "  .venv\\Scripts\\pip install spacy"
            )

    # ── Public API ───────────────────────────────────────────────────────────

    def extract(self, text: str, source: str = "") -> List[Entity]:
        """
        Extract named entities from a text string.

        Args:
            text:   Input text to process.
            source: Optional source document name for metadata.

        Returns:
            List of Entity objects (deduplicated by text+label).
        """
        if not text or not text.strip():
            return []

        doc = self.nlp(text)
        seen = set()
        entities = []

        for ent in doc.ents:
            if ent.label_ not in RELEVANT_LABELS:
                continue

            # Normalize: lowercase, strip whitespace, remove extra spaces
            normalized = re.sub(r"\s+", " ", ent.text.lower().strip())

            # Skip very short entities (likely noise)
            if len(normalized) < 2:
                continue

            # Skip pure numbers for most labels
            if ent.label_ not in {"DATE", "MONEY", "PERCENT", "QUANTITY", "CARDINAL", "ORDINAL"}:
                if normalized.replace(" ", "").isdigit():
                    continue

            entity = Entity(
                text=ent.text.strip(),
                label=ent.label_,
                normalized=normalized,
                start_char=ent.start_char,
                end_char=ent.end_char,
                source=source,
            )

            dedup_key = (normalized, ent.label_)
            if dedup_key not in seen:
                seen.add(dedup_key)
                entities.append(entity)

        return entities

    def extract_from_segments(
        self,
        segments,  # List[TextSegment] from document_processor
        verbose: bool = True,
    ) -> Dict[str, List[Entity]]:
        """
        Extract entities from a list of TextSegment objects.

        Args:
            segments: List of TextSegment objects from DocumentProcessor.
            verbose:  Print progress.

        Returns:
            Dict mapping source file name → list of unique entities.
        """
        results: Dict[str, List[Entity]] = {}

        for i, seg in enumerate(segments):
            if verbose and i % 10 == 0:
                print(f"  NER: processing segment {i + 1}/{len(segments)}...")

            entities = self.extract(seg.content, source=seg.source)

            if seg.source not in results:
                results[seg.source] = []

            # Merge and deduplicate across segments for same document
            existing_keys = {
                (e.normalized, e.label) for e in results[seg.source]
            }
            for ent in entities:
                key = (ent.normalized, ent.label)
                if key not in existing_keys:
                    results[seg.source].append(ent)
                    existing_keys.add(key)

        if verbose:
            total = sum(len(v) for v in results.values())
            print(f"  ✅ NER complete: {total} unique entities across {len(results)} document(s)")

        return results

    def group_by_label(self, entities: List[Entity]) -> Dict[str, List[Entity]]:
        """Group a list of entities by their label type."""
        groups: Dict[str, List[Entity]] = {}
        for ent in entities:
            groups.setdefault(ent.label, []).append(ent)
        return groups

    def summary(self, entities: List[Entity]) -> str:
        """Return a human-readable summary of extracted entities."""
        groups = self.group_by_label(entities)
        lines = [f"📋 Entity Summary ({len(entities)} total):"]
        for label, ents in sorted(groups.items()):
            names = ", ".join(e.text for e in ents[:5])
            more  = f" (+{len(ents) - 5} more)" if len(ents) > 5 else ""
            lines.append(f"  {label:15s} [{len(ents):3d}]: {names}{more}")
        return "\n".join(lines)


# ── Convenience function ──────────────────────────────────────────────────────

def extract_entities(text: str, model: str = "en_core_web_lg") -> List[Entity]:
    """Quick one-shot entity extraction from text."""
    extractor = NERExtractor(model=model)
    return extractor.extract(text)
