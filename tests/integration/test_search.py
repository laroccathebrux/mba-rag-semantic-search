"""
Testes de integração para o módulo search.py.

Este módulo contém testes que verificam o pipeline completo de busca
semântica com serviços externos mockados (OpenAI API, PostgreSQL/pgVector).

Os testes simulam o fluxo completo:
    1. Inicialização dos componentes (embeddings, vector store, LLM)
    2. Busca de similaridade no banco vetorial
    3. Construção do contexto a partir dos documentos relevantes
    4. Geração de resposta pelo LLM baseada no contexto

Classes de teste:
    TestSearchPromptIntegration: Testes de integração para search_prompt.
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
        """
        Testa o pipeline completo de busca com serviços externos mockados.

        Cenário: Usuário faz pergunta sobre conteúdo presente no documento.
        Esperado: Sistema retorna resposta gerada pelo LLM baseada no contexto
                  recuperado via busca de similaridade.
        """
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
        """
        Testa que search_prompt retorna True quando nenhuma pergunta é fornecida.

        Cenário: Chat inicializa o sistema sem fazer uma pergunta ainda.
        Esperado: Função retorna True indicando que a inicialização foi bem-sucedida
                  sem executar busca ou chamar o LLM.
        """
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
        """
        Testa que search_prompt retorna None para pergunta vazia.

        Cenário: Usuário envia pergunta contendo apenas espaços em branco.
        Esperado: Função retorna None indicando que não há pergunta válida
                  para processar.
        """
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
        """
        Testa tratamento de erro de conexão com banco de dados.

        Cenário: PostgreSQL não está disponível quando o usuário faz uma pergunta.
        Esperado: Função retorna None indicando erro (falha tratada graciosamente).
        """
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
        """
        Testa resposta para pergunta fora do contexto do documento.

        Cenário: Usuário faz pergunta sobre assunto não presente no documento
                 (ex: "Qual a capital da França?").
        Esperado: LLM retorna a mensagem padrão "Não tenho informações necessárias
                  para responder sua pergunta." conforme especificado no prompt.
        """
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
