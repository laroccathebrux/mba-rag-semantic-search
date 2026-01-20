"""
Testes de integração para o módulo ingest.py.

Este módulo contém testes que verificam o pipeline completo de ingestão
de documentos PDF com serviços externos mockados (OpenAI API, PostgreSQL/pgVector).

Os testes simulam o fluxo completo:
    1. Carregamento do PDF via PyPDFLoader
    2. Geração de embeddings via OpenAI API
    3. Armazenamento no PostgreSQL com pgVector

Classes de teste:
    TestIngestPdfIntegration: Testes de integração para ingest_pdf.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestIngestPdfIntegration:
    """Testes de integração para a função ingest_pdf."""

    def test_ingest_pdf_full_pipeline(self, tmp_path):
        """
        Testa o pipeline completo de ingestão com serviços externos mockados.

        Cenário: Documento PDF válido é processado pelo pipeline completo.
        Esperado: PDF é carregado, fragmentado, embeddings são gerados e
                  armazenados no banco de dados vetorial.
        """
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        # Mock dos documentos retornados pelo loader
        mock_documents = [
            Document(page_content="Test content for ingestion " * 100, metadata={"page": 0})
        ]

        with patch.dict(os.environ, {
            "PDF_PATH": str(pdf_path),
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            # Recarregar módulo para pegar novas variáveis de ambiente
            import importlib
            import ingest
            importlib.reload(ingest)

            # Aplicar patches após reload
            with patch.object(ingest, "PyPDFLoader") as mock_loader_class, \
                 patch.object(ingest, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(ingest, "PGVector") as mock_pgvector_class:

                # Configurar mock do loader
                mock_loader = MagicMock()
                mock_loader.load.return_value = mock_documents
                mock_loader_class.return_value = mock_loader

                # Configurar mock dos embeddings
                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                # Configurar mock do vector store
                mock_vector_store = MagicMock()
                mock_pgvector_class.from_documents.return_value = mock_vector_store

                # Executar ingestão
                count = ingest.ingest_pdf()

                # Verificar que todas as etapas foram executadas
                mock_loader_class.assert_called_once()
                mock_loader.load.assert_called_once()
                mock_embeddings_class.assert_called_once()
                mock_pgvector_class.from_documents.assert_called_once()
                assert count > 0

    def test_ingest_pdf_empty_pdf(self, tmp_path):
        """
        Testa ingestão com PDF que não contém texto extraível.

        Cenário: Arquivo PDF existe mas não contém texto (ex: apenas imagens).
        Esperado: Sistema lança ValueError com mensagem explicativa.
        """
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.touch()

        with patch.dict(os.environ, {
            "PDF_PATH": str(pdf_path),
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import ingest
            importlib.reload(ingest)

            with patch.object(ingest, "PyPDFLoader") as mock_loader_class:
                # Mock retorna lista vazia (PDF sem texto)
                mock_loader = MagicMock()
                mock_loader.load.return_value = []
                mock_loader_class.return_value = mock_loader

                with pytest.raises(ValueError) as exc_info:
                    ingest.ingest_pdf()

                assert "não contém texto" in str(exc_info.value)

    def test_ingest_pdf_file_not_found(self):
        """
        Testa ingestão com arquivo PDF inexistente.

        Cenário: Usuário configura PDF_PATH com caminho para arquivo que não existe.
        Esperado: Sistema lança FileNotFoundError com mensagem amigável.
        """
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

    def test_ingest_pdf_database_connection_error(self, tmp_path):
        """
        Testa tratamento de erro de conexão com banco de dados.

        Cenário: PostgreSQL não está disponível ou credenciais são inválidas.
        Esperado: Sistema lança ConnectionError com mensagem indicando problema
                  de conexão com o banco de dados.
        """
        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        mock_documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]

        with patch.dict(os.environ, {
            "PDF_PATH": str(pdf_path),
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import ingest
            importlib.reload(ingest)

            with patch.object(ingest, "PyPDFLoader") as mock_loader_class, \
                 patch.object(ingest, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(ingest, "PGVector") as mock_pgvector_class:

                mock_loader = MagicMock()
                mock_loader.load.return_value = mock_documents
                mock_loader_class.return_value = mock_loader

                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                # Simular erro de conexão
                mock_pgvector_class.from_documents.side_effect = Exception("connection refused")

                with pytest.raises(ConnectionError) as exc_info:
                    ingest.ingest_pdf()

                assert "banco de dados" in str(exc_info.value)
