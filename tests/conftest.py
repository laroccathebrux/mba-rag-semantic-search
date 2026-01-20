"""
Fixtures compartilhadas para testes do sistema RAG.

Este módulo contém fixtures reutilizáveis para os testes unitários,
de integração e de contrato do sistema de busca semântica RAG.

As fixtures incluem:
    - Mocks para embeddings OpenAI
    - Mocks para LLM (modelo de linguagem)
    - Documentos de exemplo para testes
    - Configurações de ambiente para testes
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_embeddings():
    """
    Cria mock de embeddings OpenAI que retorna um vetor fixo.

    Retorna:
        MagicMock: Mock configurado para simular OpenAIEmbeddings.

    Nota:
        O vetor retornado tem 1536 dimensões (padrão text-embedding-3-small).
    """
    mock = MagicMock()
    mock.embed_documents.return_value = [[0.1] * 1536 for _ in range(10)]
    mock.embed_query.return_value = [0.1] * 1536
    return mock


@pytest.fixture
def mock_llm():
    """
    Cria mock de LLM que retorna uma resposta predeterminada.

    Retorna:
        MagicMock: Mock configurado para simular ChatOpenAI.

    Nota:
        A resposta padrão simula uma resposta válida baseada no contexto.
    """
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Esta é uma resposta de teste baseada no contexto."
    mock.invoke.return_value = mock_response
    return mock


@pytest.fixture
def mock_llm_no_info():
    """
    Cria mock de LLM que retorna a resposta padrão de 'sem informação'.

    Retorna:
        MagicMock: Mock configurado para simular resposta fora do contexto.

    Nota:
        Usado para testar cenários onde a pergunta está fora do contexto
        do documento e o sistema deve retornar a mensagem padrão.
    """
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Não tenho informações necessárias para responder sua pergunta."
    mock.invoke.return_value = mock_response
    return mock


@pytest.fixture
def sample_documents():
    """
    Cria objetos Document de exemplo para testes.

    Retorna:
        list[Document]: Lista com 3 documentos de teste simulando
        páginas de um PDF carregado.
    """
    return [
        Document(page_content="Este é o primeiro documento de teste.", metadata={"page": 0}),
        Document(page_content="Este é o segundo documento de teste.", metadata={"page": 0}),
        Document(page_content="Este é o terceiro documento de teste.", metadata={"page": 1}),
    ]


@pytest.fixture
def sample_chunks():
    """
    Cria objetos Document fragmentados (chunks) para testes.

    Retorna:
        list[Document]: Lista com 3 chunks simulando resultado do
        RecursiveCharacterTextSplitter.
    """
    return [
        Document(page_content="Chunk 1 com conteúdo de teste.", metadata={"page": 0, "chunk": 0}),
        Document(page_content="Chunk 2 com mais conteúdo.", metadata={"page": 0, "chunk": 1}),
        Document(page_content="Chunk 3 final.", metadata={"page": 1, "chunk": 2}),
    ]


@pytest.fixture
def sample_search_results(sample_chunks):
    """
    Cria resultados de busca de exemplo com scores de similaridade.

    Args:
        sample_chunks: Fixture de chunks de exemplo.

    Retorna:
        list[tuple[Document, float]]: Lista de tuplas (documento, score)
        simulando resultado de similarity_search_with_score.
    """
    return [(chunk, 0.9 - i * 0.1) for i, chunk in enumerate(sample_chunks)]


@pytest.fixture
def mock_vector_store(sample_search_results):
    """
    Cria mock do PGVector store.

    Args:
        sample_search_results: Fixture de resultados de busca.

    Retorna:
        MagicMock: Mock configurado para simular PGVector com
        método similarity_search_with_score.
    """
    mock = MagicMock()
    mock.similarity_search_with_score.return_value = sample_search_results
    return mock


@pytest.fixture
def test_db_url():
    """
    Retorna URL de banco de dados para testes.

    Retorna:
        str: URL do banco de dados de teste, obtida da variável
        de ambiente TEST_DATABASE_URL ou valor padrão.
    """
    return os.getenv("TEST_DATABASE_URL", "postgresql://testuser:testpass@localhost:5432/rag_test")


@pytest.fixture
def temp_pdf(tmp_path):
    """
    Cria um arquivo PDF temporário para testes.

    Args:
        tmp_path: Fixture do pytest que fornece diretório temporário.

    Retorna:
        str: Caminho absoluto para o PDF temporário criado.

    Nota:
        O PDF criado tem uma página em branco e é válido para testes
        que verificam se o arquivo existe.
    """
    from pypdf import PdfWriter

    pdf_path = tmp_path / "test_document.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)


@pytest.fixture
def env_vars(test_db_url, tmp_path):
    """
    Configura variáveis de ambiente para testes.

    Args:
        test_db_url: Fixture com URL do banco de dados de teste.
        tmp_path: Fixture do pytest que fornece diretório temporário.

    Yields:
        None: Context manager que mantém as variáveis configuradas
        durante a execução do teste.

    Nota:
        As variáveis configuradas incluem: OPENAI_API_KEY, DATABASE_URL,
        PG_VECTOR_COLLECTION_NAME, PDF_PATH e OPENAI_EMBEDDING_MODEL.
    """
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
