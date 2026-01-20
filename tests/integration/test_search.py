"""
Testes de integração para o módulo search.py.

Estes testes verificam o pipeline completo de busca semântica com
serviços externos mockados (OpenAI API, PostgreSQL/pgVector).
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestSearchPromptIntegration:
    """Testes de integração para a função search_prompt."""

    def test_search_prompt_full_pipeline(self):
        """Testa o pipeline completo de busca com serviços externos mockados."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            # Recarregar módulo para pegar novas variáveis de ambiente
            import importlib
            import search
            importlib.reload(search)

            # Aplicar patches após reload
            with patch.object(search, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(search, "PGVector") as mock_pgvector_class, \
                 patch.object(search, "ChatOpenAI") as mock_llm_class:

                # Configurar mock dos embeddings
                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                # Configurar mock do vector store
                mock_vector_store = MagicMock()
                mock_vector_store.similarity_search_with_score.return_value = [
                    (Document(page_content="O faturamento foi de 10 milhões."), 0.9),
                    (Document(page_content="A empresa possui 150 funcionários."), 0.85),
                ]
                mock_pgvector_class.return_value = mock_vector_store

                # Configurar mock do LLM
                mock_response = MagicMock()
                mock_response.content = "O faturamento foi de 10 milhões de reais."
                mock_llm = MagicMock()
                mock_llm.invoke.return_value = mock_response
                mock_llm_class.return_value = mock_llm

                # Executar busca
                result = search.search_prompt("Qual o faturamento da empresa?")

                # Verificar resultado
                assert result == "O faturamento foi de 10 milhões de reais."
                mock_vector_store.similarity_search_with_score.assert_called_once()
                mock_llm.invoke.assert_called_once()

    def test_search_prompt_initialization_only(self):
        """Testa que search_prompt retorna True quando nenhuma pergunta é fornecida."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            with patch.object(search, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(search, "PGVector") as mock_pgvector_class, \
                 patch.object(search, "ChatOpenAI") as mock_llm_class:

                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                mock_vector_store = MagicMock()
                mock_pgvector_class.return_value = mock_vector_store

                mock_llm = MagicMock()
                mock_llm_class.return_value = mock_llm

                # Chamar sem pergunta
                result = search.search_prompt()

                # Verificar que retorna True (inicialização OK)
                assert result is True
                mock_vector_store.similarity_search_with_score.assert_not_called()
                mock_llm.invoke.assert_not_called()

    def test_search_prompt_empty_question(self):
        """Testa que search_prompt retorna None para pergunta vazia."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            with patch.object(search, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(search, "PGVector") as mock_pgvector_class, \
                 patch.object(search, "ChatOpenAI") as mock_llm_class:

                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                mock_vector_store = MagicMock()
                mock_pgvector_class.return_value = mock_vector_store

                mock_llm = MagicMock()
                mock_llm_class.return_value = mock_llm

                # Chamar com pergunta vazia
                result = search.search_prompt("   ")

                # Verificar que retorna None
                assert result is None

    def test_search_prompt_database_connection_error(self):
        """Testa tratamento de erro de conexão com banco de dados."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            with patch.object(search, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(search, "PGVector") as mock_pgvector_class:

                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                # Simular erro de conexão
                mock_pgvector_class.side_effect = Exception("connection refused")

                # Chamar e verificar que retorna None (erro tratado)
                result = search.search_prompt("Qual o faturamento?")

                assert result is None

    def test_search_prompt_out_of_context_response(self):
        """Testa resposta para pergunta fora do contexto do documento."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PG_VECTOR_COLLECTION_NAME": "test_collection",
        }):
            import importlib
            import search
            importlib.reload(search)

            with patch.object(search, "OpenAIEmbeddings") as mock_embeddings_class, \
                 patch.object(search, "PGVector") as mock_pgvector_class, \
                 patch.object(search, "ChatOpenAI") as mock_llm_class:

                mock_embeddings = MagicMock()
                mock_embeddings_class.return_value = mock_embeddings

                mock_vector_store = MagicMock()
                mock_vector_store.similarity_search_with_score.return_value = [
                    (Document(page_content="Informação sobre a empresa."), 0.3),
                ]
                mock_pgvector_class.return_value = mock_vector_store

                # LLM retorna resposta padrão para pergunta fora do contexto
                mock_response = MagicMock()
                mock_response.content = "Não tenho informações necessárias para responder sua pergunta."
                mock_llm = MagicMock()
                mock_llm.invoke.return_value = mock_response
                mock_llm_class.return_value = mock_llm

                result = search.search_prompt("Qual a capital da França?")

                assert "Não tenho informações" in result
