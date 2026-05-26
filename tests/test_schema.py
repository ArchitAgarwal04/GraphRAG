"""
tests/test_schema.py
Tests for US-205: Knowledge Graph Schema
"""
import pytest
from graph.schema import (
    NODE_LABELS,
    RELATIONSHIP_TYPES,
    CONSTRAINTS,
    INDEXES,
    SchemaManager,
    get_node_label,
    SPACY_LABEL_TO_NODE,
)


class TestNodeLabels:
    def test_core_labels_defined(self):
        required = ["Document", "Person", "Organization", "Location", "Entity"]
        for label in required:
            assert label in NODE_LABELS, f"Missing node label: {label}"

    def test_all_labels_have_descriptions(self):
        for label, desc in NODE_LABELS.items():
            assert isinstance(desc, str) and len(desc) > 0


class TestRelationshipTypes:
    def test_core_relations_defined(self):
        required = ["MENTIONS", "FOUNDED", "WORKS_AT", "LOCATED_IN", "APPEARS_WITH"]
        for rel in required:
            assert rel in RELATIONSHIP_TYPES, f"Missing relation: {rel}"

    def test_relations_are_uppercase(self):
        for rel in RELATIONSHIP_TYPES:
            assert rel == rel.upper(), f"Relation should be uppercase: {rel}"


class TestConstraints:
    def test_constraints_list_nonempty(self):
        assert len(CONSTRAINTS) > 0

    def test_constraints_are_cypher_strings(self):
        for c in CONSTRAINTS:
            assert "CONSTRAINT" in c or "CREATE" in c

    def test_all_constraints_have_if_not_exists(self):
        for c in CONSTRAINTS:
            assert "IF NOT EXISTS" in c, f"Constraint missing IF NOT EXISTS: {c}"


class TestIndexes:
    def test_indexes_list_nonempty(self):
        assert len(INDEXES) > 0

    def test_indexes_have_if_not_exists(self):
        for idx in INDEXES:
            assert "IF NOT EXISTS" in idx


class TestGetNodeLabel:
    def test_person_mapping(self):
        assert get_node_label("PERSON") == "Person"

    def test_org_mapping(self):
        assert get_node_label("ORG") == "Organization"

    def test_gpe_mapping(self):
        assert get_node_label("GPE") == "Location"

    def test_loc_mapping(self):
        assert get_node_label("LOC") == "Location"

    def test_date_mapping(self):
        assert get_node_label("DATE") == "Date"

    def test_product_mapping(self):
        assert get_node_label("PRODUCT") == "Product"

    def test_unknown_label_fallback(self):
        result = get_node_label("UNKNOWN_LABEL")
        assert result == "Entity"

    def test_case_insensitive(self):
        assert get_node_label("person") == get_node_label("PERSON")

    def test_all_spacy_labels_mapped(self):
        for spacy_label in SPACY_LABEL_TO_NODE:
            result = get_node_label(spacy_label)
            assert result in NODE_LABELS, f"Label {spacy_label} maps to unknown node: {result}"
