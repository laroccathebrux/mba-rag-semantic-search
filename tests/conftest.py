"""Shared fixtures for RAG system tests."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_embeddings():
    """Create mock OpenAI embeddings that return a fixed vector."""
    mock = MagicMock()
    mock.embed_documents.return_value = [[0.1] * 1536 for _ in range(10)]
    mock.embed_query.return_value = [0.1] * 1536
    return mock


@pytest.fixture
def mock_llm():
    """Create mock LLM that returns a predetermined response."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Esta é uma resposta de teste baseada no contexto."
    mock.invoke.return_value = mock_response
    return mock


@pytest.fixture
def mock_llm_no_info():
    """Create mock LLM that returns the 'no information' response."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Não tenho informações necessárias para responder sua pergunta."
    mock.invoke.return_value = mock_response
    return mock


@pytest.fixture
def sample_documents():
    """Create sample Document objects for testing."""
    return [
        Document(page_content="Este é o primeiro documento de teste.", metadata={"page": 0}),
        Document(page_content="Este é o segundo documento de teste.", metadata={"page": 0}),
        Document(page_content="Este é o terceiro documento de teste.", metadata={"page": 1}),
    ]


@pytest.fixture
def sample_chunks():
    """Create sample chunked Document objects for testing."""
    return [
        Document(page_content="Chunk 1 com conteúdo de teste.", metadata={"page": 0, "chunk": 0}),
        Document(page_content="Chunk 2 com mais conteúdo.", metadata={"page": 0, "chunk": 1}),
        Document(page_content="Chunk 3 final.", metadata={"page": 1, "chunk": 2}),
    ]


@pytest.fixture
def sample_search_results(sample_chunks):
    """Create sample search results with scores."""
    return [(chunk, 0.9 - i * 0.1) for i, chunk in enumerate(sample_chunks)]


@pytest.fixture
def mock_vector_store(sample_search_results):
    """Create mock PGVector store."""
    mock = MagicMock()
    mock.similarity_search_with_score.return_value = sample_search_results
    return mock


@pytest.fixture
def test_db_url():
    """Return test database URL from environment or use test defaults."""
    return os.getenv("TEST_DATABASE_URL", "postgresql://testuser:testpass@localhost:5432/rag_test")


@pytest.fixture
def temp_pdf(tmp_path):
    """Create a temporary PDF file for testing."""
    from pypdf import PdfWriter

    pdf_path = tmp_path / "test_document.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)


@pytest.fixture
def env_vars(test_db_url, tmp_path):
    """Set up environment variables for testing."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()

    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-api-key",
        "DATABASE_URL": test_db_url,
        "PG_VECTOR_COLLECTION_NAME": "test_chunks",
        "PDF_PATH": str(pdf_path),
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
    }):
        yield
