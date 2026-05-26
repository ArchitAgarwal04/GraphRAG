"""
extraction/llm_extractor.py
US-203 — LLM-Powered Relationship Extraction

Uses Groq (Llama 3.1) to extract Subject → Relationship → Object
triples from text. These triples become edges in the knowledge graph.

Acceptance Criteria:
  - Relationships stored with correct mapping
  - Create relation extraction logic
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Triple:
    """
    A Subject → Relationship → Object triple extracted from text.
    Becomes one edge in the knowledge graph.

    Example:
        Triple("Elon Musk", "FOUNDED", "Tesla", "Elon Musk founded Tesla.")
    """
    subject: str          # Entity A (e.g., "Elon Musk")
    relation: str         # Relationship type (e.g., "FOUNDED")
    obj: str              # Entity B (e.g., "Tesla")
    source_text: str = "" # Original sentence for traceability
    source_doc: str = ""  # Source document name
    confidence: float = 1.0

    def __repr__(self) -> str:
        return f"Triple({self.subject!r} --[{self.relation}]--> {self.obj!r})"

    def to_dict(self) -> dict:
        return {
            "subject":     self.subject,
            "relation":    self.relation,
            "object":      self.obj,
            "source_text": self.source_text,
            "source_doc":  self.source_doc,
        }


# ── Prompts ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a knowledge graph extraction expert. Your job is to extract 
subject-relation-object triples from the given text.

Rules:
1. Extract ONLY factual relationships explicitly stated in the text.
2. Use concise, UPPERCASE relation types (e.g., FOUNDED, LOCATED_IN, WORKS_AT, ACQUIRED, PARTNER_OF, CEO_OF).
3. Normalize entities: use full proper names, consistent capitalization.
4. Return ONLY valid JSON — no explanation, no markdown, no extra text.
5. If no relationships are found, return {"triples": []}.

Output format:
{
  "triples": [
    {"subject": "...", "relation": "...", "object": "..."},
    ...
  ]
}"""

USER_PROMPT_TEMPLATE = """Extract subject-relation-object triples from this text:

TEXT:
{text}

Return JSON only."""


class LLMRelationExtractor:
    """
    US-203: LLM-powered relationship extraction using Groq.

    Sends text to Groq LLM and parses structured JSON triples.

    Usage:
        extractor = LLMRelationExtractor()
        triples = extractor.extract("Apple was founded by Steve Jobs in 1976.")
    """

    def __init__(
        self,
        model: str = None,
        api_key: str = None,
        max_text_length: int = 2000,
    ):
        self.model           = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.api_key         = api_key or os.getenv("GROQ_API_KEY", "")
        self.max_text_length = max_text_length
        self._llm            = None

    def _get_llm(self):
        """Lazy-load the Groq LLM."""
        if self._llm is None:
            try:
                from langchain_groq import ChatGroq
            except ImportError:
                raise ImportError(
                    "langchain-groq not installed.\n"
                    "Run: .venv\\Scripts\\pip install langchain-groq"
                )
            if not self.api_key:
                raise ValueError(
                    "GROQ_API_KEY not set.\n"
                    "Add it to your .env file or set the environment variable."
                )
            self._llm = ChatGroq(
                model=self.model,
                api_key=self.api_key,
                temperature=0,       # deterministic for extraction
                max_retries=3,
            )
        return self._llm

    # ── Public API ────────────────────────────────────────────────────────────

    def extract(self, text: str, source_doc: str = "") -> List[Triple]:
        """
        Extract relationship triples from a text string.

        Args:
            text:       Input text to analyse.
            source_doc: Optional document name for metadata.

        Returns:
            List of Triple objects.
        """
        if not text or not text.strip():
            return []

        # Truncate to avoid token limits
        text = text[: self.max_text_length]

        llm    = self._get_llm()
        prompt = USER_PROMPT_TEMPLATE.format(text=text.strip())

        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        try:
            response = llm.invoke(messages)
            raw      = response.content.strip()
            triples  = self._parse_response(raw, text, source_doc)
            return triples
        except Exception as e:
            print(f"  ⚠️  LLM extraction failed: {e}")
            return []

    def extract_from_segments(
        self,
        segments,
        verbose: bool = True,
        batch_size: int = 1,
    ) -> List[Triple]:
        """
        Extract triples from a list of TextSegment objects.

        Args:
            segments:   TextSegment list from DocumentProcessor.
            verbose:    Print progress.
            batch_size: Segments per LLM call (1 = safest).

        Returns:
            All extracted triples across all segments.
        """
        all_triples: List[Triple] = []

        for i, seg in enumerate(segments):
            if verbose:
                print(f"  LLM: extracting from segment {i + 1}/{len(segments)}...", end="\r")

            triples = self.extract(seg.content, source_doc=seg.source)
            all_triples.extend(triples)

        if verbose:
            print(f"\n  ✅ LLM extraction complete: {len(all_triples)} triples found")

        # Deduplicate
        seen    = set()
        unique  = []
        for t in all_triples:
            key = (t.subject.lower(), t.relation.upper(), t.obj.lower())
            if key not in seen:
                seen.add(key)
                unique.append(t)

        if verbose and len(unique) < len(all_triples):
            print(f"  🔁 Deduplicated: {len(all_triples)} → {len(unique)} unique triples")

        return unique

    # ── Private helpers ───────────────────────────────────────────────────────

    def _parse_response(
        self,
        raw: str,
        source_text: str,
        source_doc: str,
    ) -> List[Triple]:
        """Parse the LLM JSON response into Triple objects."""

        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON substring
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    return []
            else:
                return []

        raw_triples = data.get("triples", [])
        if not isinstance(raw_triples, list):
            return []

        triples = []
        for item in raw_triples:
            if not isinstance(item, dict):
                continue
            subj = str(item.get("subject", "")).strip()
            rel  = str(item.get("relation", "")).strip().upper().replace(" ", "_")
            obj  = str(item.get("object",  "")).strip()

            if subj and rel and obj and subj.lower() != obj.lower():
                triples.append(
                    Triple(
                        subject=subj,
                        relation=rel,
                        obj=obj,
                        source_text=source_text[:200],
                        source_doc=source_doc,
                    )
                )

        return triples

    def summary(self, triples: List[Triple]) -> str:
        """Return a human-readable summary of extracted triples."""
        if not triples:
            return "No triples extracted."
        lines = [f"🔗 Relationship Summary ({len(triples)} triples):"]
        for t in triples[:20]:
            lines.append(f"  {t.subject} --[{t.relation}]--> {t.obj}")
        if len(triples) > 20:
            lines.append(f"  ... and {len(triples) - 20} more")
        return "\n".join(lines)


# ── Convenience function ──────────────────────────────────────────────────────

def extract_relations(text: str) -> List[Triple]:
    """Quick one-shot relationship extraction from text."""
    extractor = LLMRelationExtractor()
    return extractor.extract(text)
