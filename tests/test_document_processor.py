"""
tests/test_document_processor.py
Tests for US-201: Document Ingestion Pipeline
"""
import os
import pytest
from pathlib import Path
from pipeline.document_processor import DocumentProcessor, TextSegment, load_documents


SAMPLE_TEXT = """Apple was founded by Steve Jobs in 1976 in Cupertino, California.
Microsoft was founded by Bill Gates and Paul Allen in 1975.
Google was started by Larry Page and Sergey Brin at Stanford University."""


@pytest.fixture
def processor():
    return DocumentProcessor(chunk_size=500, chunk_overlap=50)


@pytest.fixture
def sample_txt_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text(SAMPLE_TEXT, encoding="utf-8")
    return str(f)


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestTextSegment:
    def test_segment_creation(self):
        seg = TextSegment(content="Hello World", source="test.txt", page=1)
        assert seg.content == "Hello World"
        assert seg.source  == "test.txt"
        assert seg.page    == 1

    def test_segment_repr(self):
        seg = TextSegment(content="Hello World", source="test.txt")
        assert "test.txt" in repr(seg)


class TestDocumentProcessorTxt:
    def test_load_txt(self, processor, sample_txt_file):
        segments = processor.process_file(sample_txt_file)
        assert len(segments) >= 1
        assert all(isinstance(s, TextSegment) for s in segments)

    def test_segment_has_content(self, processor, sample_txt_file):
        segments = processor.process_file(sample_txt_file)
        for seg in segments:
            assert len(seg.content) > 0

    def test_segment_source_name(self, processor, sample_txt_file):
        segments = processor.process_file(sample_txt_file)
        for seg in segments:
            assert seg.source == "test.txt"

    def test_segment_file_type(self, processor, sample_txt_file):
        segments = processor.process_file(sample_txt_file)
        for seg in segments:
            assert seg.file_type == "txt"

    def test_file_not_found(self, processor):
        with pytest.raises(FileNotFoundError):
            processor.process_file("nonexistent_file.txt")

    def test_unsupported_extension(self, processor, tmp_path):
        f = tmp_path / "test.xyz"
        f.write_text("content")
        with pytest.raises(ValueError, match="Unsupported file type"):
            processor.process_file(str(f))

    def test_empty_file(self, processor, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        segments = processor.process_file(str(f))
        assert segments == []


class TestChunking:
    def test_short_text_single_chunk(self, processor):
        short = "This is a short text."
        chunks = processor._chunk_text(short)
        assert len(chunks) == 1
        assert chunks[0] == short

    def test_long_text_multiple_chunks(self, processor):
        long_text = "word " * 500  # 2500 chars
        chunks = processor._chunk_text(long_text)
        assert len(chunks) > 1

    def test_chunks_cover_content(self, processor):
        text = "Hello World. " * 100
        chunks = processor._chunk_text(text)
        combined = " ".join(chunks)
        assert "Hello" in combined
        assert "World" in combined

    def test_empty_text_returns_empty(self, processor):
        chunks = processor._chunk_text("")
        assert chunks == []

    def test_whitespace_only_returns_empty(self, processor):
        chunks = processor._chunk_text("   \n\n\t  ")
        assert chunks == []


class TestProcessMultiple:
    def test_process_multiple_files(self, processor, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("File A content about Apple Inc.")
        f2.write_text("File B content about Google LLC.")

        segments = processor.process_multiple([str(f1), str(f2)])
        sources  = {s.source for s in segments}
        assert "a.txt" in sources
        assert "b.txt" in sources

    def test_missing_file_does_not_crash(self, processor, tmp_path):
        f1 = tmp_path / "valid.txt"
        f1.write_text("Valid content here.")
        # Should not raise — just skip the missing file
        segments = processor.process_multiple([str(f1), "missing_file.txt"])
        assert len(segments) >= 1


class TestLoadDocumentsHelper:
    def test_load_documents_function(self, tmp_path):
        f = tmp_path / "doc.txt"
        f.write_text("Elon Musk founded SpaceX in 2002 in Hawthorne, California.")
        segments = load_documents([str(f)], chunk_size=200)
        assert len(segments) >= 1
