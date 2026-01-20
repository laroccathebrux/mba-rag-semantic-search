"""Integration tests for ingest.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestIngestPdfIntegration:
    """Integration tests for ingest_pdf function."""

    @patch("ingest.PGVector")
    @patch("ingest.OpenAIEmbeddings")
    @patch("ingest.PyPDFLoader")
    def test_ingest_pdf_full_pipeline(
        self, mock_loader_class, mock_embeddings_class, mock_pgvector_class, tmp_path
    ):
        """Test the full ingestion pipeline with mocked external services."""
        from langchain_core.documents import Document

        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        mock_loader = MagicMock()
        mock_loader.load.return_value = [
            Document(page_content="Test content for ingestion " * 100, metadata={"page": 0})
        ]
        mock_loader_class.return_value = mock_loader

        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        mock_vector_store = MagicMock()
        mock_pgvector_class.from_documents.return_value = mock_vector_store

        with patch.dict(os.environ, {
            "PDF_PATH": str(pdf_path),
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import ingest
            importlib.reload(ingest)

            count = ingest.ingest_pdf()

        mock_loader_class.assert_called_once()
        mock_embeddings_class.assert_called_once()
        mock_pgvector_class.from_documents.assert_called_once()
        assert count > 0

    @patch("ingest.PGVector")
    @patch("ingest.OpenAIEmbeddings")
    @patch("ingest.PyPDFLoader")
    def test_ingest_pdf_empty_pdf(
        self, mock_loader_class, mock_embeddings_class, mock_pgvector_class, tmp_path
    ):
        """Test ingestion with empty PDF."""
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.touch()

        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_class.return_value = mock_loader

        with patch.dict(os.environ, {
            "PDF_PATH": str(pdf_path),
            "OPENAI_API_KEY": "test-key",
        }):
            import importlib
            import ingest
            importlib.reload(ingest)

            with pytest.raises(ValueError) as exc_info:
                ingest.ingest_pdf()

            assert "não contém texto" in str(exc_info.value)

    def test_ingest_pdf_file_not_found(self, tmp_path):
        """Test ingestion with non-existent PDF."""
        with patch.dict(os.environ, {
            "PDF_PATH": "/nonexistent/path/document.pdf",
            "OPENAI_API_KEY": "test-key",
        }):
            import importlib
            import ingest
            importlib.reload(ingest)

            with pytest.raises(FileNotFoundError) as exc_info:
                ingest.ingest_pdf()

            assert "não encontrado" in str(exc_info.value)
