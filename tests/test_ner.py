"""
tests/test_ner.py
Tests for US-202: NER Pipeline
"""
import pytest
from extraction.ner import Entity, NERExtractor, extract_entities, RELEVANT_LABELS


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ner():
    """Load spaCy model once for all tests in this module."""
    return NERExtractor()  # will try lg, fallback to sm


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestEntity:
    def test_entity_creation(self):
        ent = Entity("Elon Musk", "PERSON", "elon musk", 0, 9, "doc.txt")
        assert ent.text       == "Elon Musk"
        assert ent.label      == "PERSON"
        assert ent.normalized == "elon musk"
        assert ent.source     == "doc.txt"

    def test_entity_equality(self):
        e1 = Entity("Apple", "ORG", "apple", 0, 5)
        e2 = Entity("Apple", "ORG", "apple", 10, 15)
        assert e1 == e2

    def test_entity_hash_dedup(self):
        e1 = Entity("Tesla", "ORG", "tesla", 0, 5)
        e2 = Entity("Tesla", "ORG", "tesla", 20, 25)
        entity_set = {e1, e2}
        assert len(entity_set) == 1

    def test_entity_repr(self):
        ent = Entity("Google", "ORG", "google", 0, 6)
        assert "Google" in repr(ent)
        assert "ORG"    in repr(ent)


class TestNERExtractor:
    def test_extracts_person(self, ner):
        entities = ner.extract("Steve Jobs founded Apple in California.")
        names = [e.text for e in entities]
        assert any("Steve" in n for n in names), f"Expected person in: {names}"

    def test_extracts_org(self, ner):
        entities = ner.extract("Microsoft was founded by Bill Gates.")
        labels = [e.label for e in entities]
        assert "ORG" in labels or "PERSON" in labels

    def test_extracts_location(self, ner):
        entities = ner.extract("Google is headquartered in Mountain View, California.")
        labels = [e.label for e in entities]
        assert "GPE" in labels or "LOC" in labels

    def test_empty_text_returns_empty(self, ner):
        assert ner.extract("") == []
        assert ner.extract("   ") == []

    def test_deduplication(self, ner):
        text = "Apple is a company. Apple makes iPhones. Apple is great."
        entities = ner.extract(text)
        apple_entities = [e for e in entities if e.normalized == "apple"]
        assert len(apple_entities) <= 1, "Apple should appear only once after deduplication"

    def test_returns_entity_objects(self, ner):
        entities = ner.extract("Elon Musk is the CEO of Tesla.")
        assert all(isinstance(e, Entity) for e in entities)

    def test_only_relevant_labels(self, ner):
        entities = ner.extract("Elon Musk founded SpaceX in 2002 in Hawthorne California.")
        for ent in entities:
            assert ent.label in RELEVANT_LABELS, f"Unexpected label: {ent.label}"

    def test_normalized_is_lowercase(self, ner):
        entities = ner.extract("AMAZON is a big company based in SEATTLE.")
        for ent in entities:
            assert ent.normalized == ent.normalized.lower()

    def test_source_metadata(self, ner):
        entities = ner.extract("Apple was founded in 1976.", source="test.txt")
        for ent in entities:
            assert ent.source == "test.txt"


class TestGroupByLabel:
    def test_group_by_label(self, ner):
        entities = ner.extract(
            "Elon Musk founded Tesla in 2003 in Austin, Texas."
        )
        groups = ner.group_by_label(entities)
        assert isinstance(groups, dict)
        for label, ents in groups.items():
            assert all(e.label == label for e in ents)


class TestSummary:
    def test_summary_output(self, ner):
        entities = ner.extract("Bill Gates co-founded Microsoft in 1975 in Albuquerque.")
        summary = ner.summary(entities)
        assert isinstance(summary, str)
        assert "Entity Summary" in summary


class TestExtractEntitiesHelper:
    def test_quick_extraction(self):
        entities = extract_entities("Jeff Bezos founded Amazon in 1994.")
        assert isinstance(entities, list)
