"""Integration tests for search.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestSearchPromptIntegration:
    """Integration tests for search_prompt function."""

    @patch("search.ChatOpenAI")
    @patch("search.PGVector")
    @patch("search.OpenAIEmbeddings")
    def test_search_prompt_full_pipeline(
        self, mock_embeddings_class, mock_pgvector_class, mock_llm_class
    ):
        """Test the full search pipeline with mocked external services."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        mock_vector_store = MagicMock()
        mock_vector_store.similarity_search_with_score.return_value = [
            (Document(page_content="O faturamento foi de 10 milhões."), 0.9),
            (Document(page_content="A empresa possui 150 funcionários."), 0.85),
        ]
        mock_pgvector_class.return_value = mock_vector_store

        mock_response = MagicMock()
        mock_response.content = "O faturamento foi de 10 milhões de reais."
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm

        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            result = search.search_prompt("Qual o faturamento da empresa?")

        assert result == "O faturamento foi de 10 milhões de reais."
        mock_vector_store.similarity_search_with_score.assert_called_once()
        mock_llm.invoke.assert_called_once()

    @patch("search.ChatOpenAI")
    @patch("search.PGVector")
    @patch("search.OpenAIEmbeddings")
    def test_search_prompt_initialization_only(
        self, mock_embeddings_class, mock_pgvector_class, mock_llm_class
    ):
        """Test search_prompt returns True when no question is provided."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        mock_vector_store = MagicMock()
        mock_pgvector_class.return_value = mock_vector_store

        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm

        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            result = search.search_prompt()

        assert result is True
        mock_vector_store.similarity_search_with_score.assert_not_called()
        mock_llm.invoke.assert_not_called()

    @patch("search.ChatOpenAI")
    @patch("search.PGVector")
    @patch("search.OpenAIEmbeddings")
    def test_search_prompt_empty_question(
        self, mock_embeddings_class, mock_pgvector_class, mock_llm_class
    ):
        """Test search_prompt returns None for empty question."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        mock_vector_store = MagicMock()
        mock_pgvector_class.return_value = mock_vector_store

        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm

        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            result = search.search_prompt("   ")

        assert result is None
