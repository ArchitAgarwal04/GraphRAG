"""
tests/test_llm_extractor.py
Tests for US-203: LLM Relationship Extraction
"""
import json
import pytest
from extraction.llm_extractor import Triple, LLMRelationExtractor


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestTriple:
    def test_triple_creation(self):
        t = Triple("Elon Musk", "FOUNDED", "Tesla", "Elon Musk founded Tesla.")
        assert t.subject      == "Elon Musk"
        assert t.relation     == "FOUNDED"
        assert t.obj          == "Tesla"
        assert t.source_text  == "Elon Musk founded Tesla."

    def test_triple_repr(self):
        t = Triple("Apple", "LOCATED_IN", "California")
        assert "Apple" in repr(t)
        assert "LOCATED_IN" in repr(t)
        assert "California" in repr(t)

    def test_triple_to_dict(self):
        t = Triple("Google", "FOUNDED_BY", "Larry Page", source_doc="doc.txt")
        d = t.to_dict()
        assert d["subject"]    == "Google"
        assert d["relation"]   == "FOUNDED_BY"
        assert d["object"]     == "Larry Page"
        assert d["source_doc"] == "doc.txt"


class TestParseResponse:
    """Test the JSON parsing logic without hitting the real LLM."""

    @pytest.fixture
    def extractor(self):
        return LLMRelationExtractor(api_key="fake_key_for_testing")

    def test_parse_valid_json(self, extractor):
        raw = json.dumps({
            "triples": [
                {"subject": "Elon Musk", "relation": "FOUNDED", "object": "Tesla"},
                {"subject": "Tesla", "relation": "LOCATED_IN", "object": "Austin"},
            ]
        })
        triples = extractor._parse_response(raw, "source text", "doc.txt")
        assert len(triples) == 2
        assert triples[0].subject  == "Elon Musk"
        assert triples[0].relation == "FOUNDED"
        assert triples[0].obj      == "Tesla"

    def test_parse_json_with_code_fence(self, extractor):
        raw = "```json\n" + json.dumps({"triples": [
            {"subject": "Apple", "relation": "FOUNDED_BY", "object": "Steve Jobs"}
        ]}) + "\n```"
        triples = extractor._parse_response(raw, "", "")
        assert len(triples) == 1

    def test_parse_empty_triples(self, extractor):
        raw = json.dumps({"triples": []})
        triples = extractor._parse_response(raw, "", "")
        assert triples == []

    def test_parse_invalid_json(self, extractor):
        triples = extractor._parse_response("not json at all", "", "")
        assert triples == []

    def test_parse_skips_self_relations(self, extractor):
        """Subject and object should not be the same entity."""
        raw = json.dumps({"triples": [
            {"subject": "Apple", "relation": "IS", "object": "apple"},
        ]})
        triples = extractor._parse_response(raw, "", "")
        assert len(triples) == 0

    def test_relation_uppercased(self, extractor):
        raw = json.dumps({"triples": [
            {"subject": "Google", "relation": "located in", "object": "California"},
        ]})
        triples = extractor._parse_response(raw, "", "")
        assert triples[0].relation == "LOCATED_IN"

    def test_parse_missing_fields_skipped(self, extractor):
        raw = json.dumps({"triples": [
            {"subject": "Apple"},          # missing relation and object
            {"subject": "Google", "relation": "FOUNDED_BY", "object": "Larry Page"},
        ]})
        triples = extractor._parse_response(raw, "", "")
        assert len(triples) == 1
        assert triples[0].subject == "Google"


class TestExtractorConfig:
    def test_default_model(self):
        extractor = LLMRelationExtractor(api_key="fake")
        assert "llama" in extractor.model.lower() or extractor.model != ""

    def test_custom_model(self):
        extractor = LLMRelationExtractor(model="gemma2-9b-it", api_key="fake")
        assert extractor.model == "gemma2-9b-it"

    def test_max_text_length_truncation(self):
        extractor = LLMRelationExtractor(api_key="fake", max_text_length=50)
        assert extractor.max_text_length == 50


class TestSummary:
    def test_summary_no_triples(self):
        extractor = LLMRelationExtractor(api_key="fake")
        assert extractor.summary([]) == "No triples extracted."

    def test_summary_with_triples(self):
        extractor = LLMRelationExtractor(api_key="fake")
        triples = [
            Triple("Elon Musk", "FOUNDED", "Tesla"),
            Triple("Tesla", "LOCATED_IN", "Austin"),
        ]
        summary = extractor.summary(triples)
        assert "Relationship Summary" in summary
        assert "Elon Musk" in summary
