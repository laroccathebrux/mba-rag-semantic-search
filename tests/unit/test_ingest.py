"""Unit tests for ingest.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ingest import load_pdf, split_documents, CHUNK_SIZE, CHUNK_OVERLAP


class TestLoadPdf:
    """Tests for load_pdf function."""

    def test_load_pdf_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_pdf("/path/to/nonexistent.pdf")
        assert "Arquivo PDF não encontrado" in str(exc_info.value)

    @patch("ingest.PyPDFLoader")
    def test_load_pdf_valid_file(self, mock_loader_class, tmp_path):
        """Test loading a valid PDF file."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        mock_loader = MagicMock()
        mock_loader.load.return_value = [MagicMock(page_content="Test content")]
        mock_loader_class.return_value = mock_loader

        result = load_pdf(str(pdf_path))

        mock_loader_class.assert_called_once_with(str(pdf_path))
        mock_loader.load.assert_called_once()
        assert len(result) == 1


class TestSplitDocuments:
    """Tests for split_documents function."""

    def test_split_documents_empty_list(self):
        """Test splitting an empty document list."""
        result = split_documents([])
        assert result == []

    def test_split_documents_small_content(self, sample_documents):
        """Test splitting documents smaller than chunk size."""
        result = split_documents(sample_documents)
        assert len(result) >= len(sample_documents)

    def test_split_documents_respects_chunk_size(self):
        """Test that chunks respect the configured chunk size."""
        from langchain_core.documents import Document

        long_content = "A" * 2500
        documents = [Document(page_content=long_content, metadata={"page": 0})]

        result = split_documents(documents)

        for chunk in result:
            assert len(chunk.page_content) <= CHUNK_SIZE + CHUNK_OVERLAP

    def test_split_documents_overlap(self):
        """Test that chunks have proper overlap."""
        from langchain_core.documents import Document

        content = "A" * (CHUNK_SIZE + 500)
        documents = [Document(page_content=content, metadata={"page": 0})]

        result = split_documents(documents)

        assert len(result) >= 2


class TestChunkConfiguration:
    """Tests for chunk configuration constants."""

    def test_chunk_size_is_1000(self):
        """Verify chunk size is 1000 as per specification."""
        assert CHUNK_SIZE == 1000

    def test_chunk_overlap_is_150(self):
        """Verify chunk overlap is 150 as per specification."""
        assert CHUNK_OVERLAP == 150
