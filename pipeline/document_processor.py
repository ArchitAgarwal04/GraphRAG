"""
pipeline/document_processor.py
US-201 — Document Ingestion Pipeline

Loads PDF, DOCX, and TXT files and returns clean text segments
with metadata, ready for entity extraction.

Acceptance Criteria:
  - Documents uploaded and parsed successfully
  - Text extracted with acceptable accuracy
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class TextSegment:
    """
    Represents a segment of text extracted from a document.
    Contains content plus metadata for traceability.
    """
    content: str
    source: str           # original file name
    page: int = 0         # page number (PDF) or 0 for text files
    segment_index: int = 0
    file_type: str = ""
    char_start: int = 0
    char_end: int = 0

    def __repr__(self) -> str:
        preview = self.content[:60].replace("\n", " ")
        return f"TextSegment(source={self.source!r}, page={self.page}, preview={preview!r})"


class DocumentProcessor:
    """
    US-201: Document Ingestion Pipeline

    Supports:
      - PDF  → via PyMuPDF (fitz)
      - DOCX → via python-docx
      - TXT  → plain UTF-8 read
      - MD   → treated as plain text

    Usage:
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
        segments  = processor.process_file("path/to/doc.pdf")
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """
        Args:
            chunk_size:    Maximum characters per text segment.
            chunk_overlap: Characters of overlap between consecutive segments.
        """
        self.chunk_size    = chunk_size
        self.chunk_overlap = chunk_overlap

    # ── Public API ──────────────────────────────────────────────────────────

    def process_file(self, file_path: str) -> List[TextSegment]:
        """
        Load and process a single file.

        Args:
            file_path: Absolute or relative path to the document.

        Returns:
            List of TextSegment objects.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError:        If the file type is not supported.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        if ext == ".pdf":
            raw_pages = self._load_pdf(path)
        elif ext == ".docx":
            raw_pages = self._load_docx(path)
        else:  # .txt or .md
            raw_pages = self._load_text(path)

        # Chunk each page/section into segments
        segments: List[TextSegment] = []
        for page_num, page_text in raw_pages:
            chunks = self._chunk_text(page_text)
            for i, chunk in enumerate(chunks):
                segments.append(
                    TextSegment(
                        content=chunk,
                        source=path.name,
                        page=page_num,
                        segment_index=len(segments),
                        file_type=ext.lstrip("."),
                    )
                )

        return segments

    def process_multiple(self, file_paths: List[str]) -> List[TextSegment]:
        """
        Process multiple files and merge results.

        Args:
            file_paths: List of file paths to process.

        Returns:
            Combined list of TextSegment objects from all files.
        """
        all_segments: List[TextSegment] = []
        errors: List[str] = []

        for fp in file_paths:
            try:
                segs = self.process_file(fp)
                all_segments.extend(segs)
                print(f"  ✅ Loaded {fp} → {len(segs)} segments")
            except Exception as e:
                errors.append(f"  ❌ {fp}: {e}")
                print(errors[-1])

        if errors:
            print(f"\n⚠️  {len(errors)} file(s) failed to load.")

        return all_segments

    # ── Private Loaders ─────────────────────────────────────────────────────

    def _load_pdf(self, path: Path) -> List[tuple]:
        """Extract text page-by-page from a PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

        pages = []
        with fitz.open(str(path)) as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if text:
                    pages.append((page_num, text))
        return pages

    def _load_docx(self, path: Path) -> List[tuple]:
        """Extract paragraphs from a DOCX file using python-docx."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

        doc = Document(str(path))
        full_text = "\n".join(
            para.text for para in doc.paragraphs if para.text.strip()
        )
        return [(0, full_text)]

    def _load_text(self, path: Path) -> List[tuple]:
        """Load a plain text or markdown file."""
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        return [(0, text)]

    # ── Text Chunker ─────────────────────────────────────────────────────────

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        Tries to split on paragraph/sentence boundaries.
        """
        if not text.strip():
            return []

        if len(text) <= self.chunk_size:
            return [text.strip()]

        chunks  = []
        start   = 0
        length  = len(text)

        while start < length:
            end = min(start + self.chunk_size, length)

            # Try to break at a paragraph boundary
            if end < length:
                para_break = text.rfind("\n\n", start, end)
                if para_break != -1 and para_break > start + self.chunk_size // 2:
                    end = para_break
                else:
                    # Try sentence boundary
                    sent_break = text.rfind(". ", start, end)
                    if sent_break != -1 and sent_break > start + self.chunk_size // 2:
                        end = sent_break + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = max(start + 1, end - self.chunk_overlap)

        return chunks


# ── Convenience function ─────────────────────────────────────────────────────

def load_documents(file_paths: List[str], chunk_size: int = 1000) -> List[TextSegment]:
    """
    Quick helper to load and chunk multiple documents.

    Args:
        file_paths: List of document paths.
        chunk_size: Characters per chunk.

    Returns:
        All text segments from all documents.
    """
    processor = DocumentProcessor(chunk_size=chunk_size)
    return processor.process_multiple(file_paths)
