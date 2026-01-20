"""
Testes unitários para o módulo search.py.

Este módulo contém testes para as funções de construção de contexto,
formatação de prompt e constantes de configuração do pipeline de busca
semântica do sistema RAG.

Classes de teste:
    TestBuildContext: Testes para a função build_context.
    TestFormatPrompt: Testes para a função format_prompt.
    TestPromptTemplate: Testes para a constante PROMPT_TEMPLATE.
    TestConfiguration: Testes para as constantes de configuração.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from search import build_context, format_prompt, PROMPT_TEMPLATE, SIMILARITY_K


class TestBuildContext:
    """Testes para a função build_context."""

    def test_build_context_empty_results(self):
        """
        Testa construção de contexto a partir de resultados vazios.

        Cenário: Busca semântica não retorna documentos relevantes.
        Esperado: Função retorna string vazia sem erros.
        """
        result = build_context([])
        assert result == ""

    def test_build_context_single_document(self):
        """
        Testa construção de contexto a partir de um único documento.

        Cenário: Busca semântica retorna apenas um documento relevante.
        Esperado: Contexto contém exatamente o conteúdo do documento.
        """
        doc = Document(page_content="Test content")
        results = [(doc, 0.9)]

        result = build_context(results)

        assert result == "Test content"

    def test_build_context_multiple_documents(self, sample_search_results):
        """
        Testa construção de contexto a partir de múltiplos documentos.

        Cenário: Busca semântica retorna vários documentos relevantes.
        Esperado: Contexto contém todos os documentos separados por quebras de linha.
        """
        result = build_context(sample_search_results)

        assert "\n\n" in result
        for doc, _ in sample_search_results:
            assert doc.page_content in result

    def test_build_context_preserves_order(self):
        """
        Testa que o contexto preserva a ordem dos documentos.

        Cenário: Documentos são passados em ordem específica por relevância.
        Esperado: Ordem é mantida no contexto final (mais relevante primeiro).
        """
        docs = [
            (Document(page_content="First"), 0.9),
            (Document(page_content="Second"), 0.8),
            (Document(page_content="Third"), 0.7),
        ]

        result = build_context(docs)

        first_idx = result.index("First")
        second_idx = result.index("Second")
        third_idx = result.index("Third")

        assert first_idx < second_idx < third_idx


class TestFormatPrompt:
    """Testes para a função format_prompt."""

    def test_format_prompt_includes_context(self):
        """
        Testa que o prompt formatado inclui o contexto.

        Cenário: Contexto é passado para formatação do prompt.
        Esperado: Contexto aparece no prompt final enviado ao LLM.
        """
        result = format_prompt("Test context", "Test question")
        assert "Test context" in result

    def test_format_prompt_includes_question(self):
        """
        Testa que o prompt formatado inclui a pergunta.

        Cenário: Pergunta do usuário é passada para formatação.
        Esperado: Pergunta aparece no prompt final enviado ao LLM.
        """
        result = format_prompt("Test context", "Test question")
        assert "Test question" in result

    def test_format_prompt_includes_rules(self):
        """
        Testa que o prompt formatado inclui as regras.

        Cenário: Prompt é formatado para envio ao LLM.
        Esperado: Regras de resposta baseada apenas no contexto estão presentes.
        """
        result = format_prompt("Context", "Question")
        assert "REGRAS:" in result
        assert "Responda somente com base no CONTEXTO" in result

    def test_format_prompt_includes_examples(self):
        """
        Testa que o prompt formatado inclui exemplos de perguntas fora do contexto.

        Cenário: Prompt é formatado com few-shot examples.
        Esperado: Exemplos de perguntas fora do contexto estão presentes para guiar o LLM.
        """
        result = format_prompt("Context", "Question")
        assert "capital da França" in result
        assert "Você acha isso bom ou ruim" in result


class TestPromptTemplate:
    """Testes para a constante PROMPT_TEMPLATE."""

    def test_prompt_template_has_contexto_placeholder(self):
        """
        Testa que o template possui placeholder {contexto}.

        Cenário: Validação da estrutura do template.
        Esperado: Template contém {contexto} para interpolação.
        """
        assert "{contexto}" in PROMPT_TEMPLATE

    def test_prompt_template_has_pergunta_placeholder(self):
        """
        Testa que o template possui placeholder {pergunta}.

        Cenário: Validação da estrutura do template.
        Esperado: Template contém {pergunta} para interpolação.
        """
        assert "{pergunta}" in PROMPT_TEMPLATE

    def test_prompt_template_has_no_info_response(self):
        """
        Testa que o template inclui a resposta padrão de 'sem informação'.

        Cenário: Validação do comportamento para perguntas fora do contexto.
        Esperado: Mensagem padrão está presente no template como instrução ao LLM.
        """
        assert "Não tenho informações necessárias para responder sua pergunta" in PROMPT_TEMPLATE

    def test_prompt_template_has_three_examples(self):
        """
        Testa que o template possui exatamente três exemplos.

        Cenário: Validação dos few-shot examples no template.
        Esperado: Existem 3 exemplos de perguntas fora do contexto (requisito do desafio).
        """
        examples = PROMPT_TEMPLATE.count("Resposta: \"Não tenho informações")
        assert examples == 3


class TestConfiguration:
    """Testes para as constantes de configuração de busca."""

    def test_similarity_k_is_10(self):
        """
        Verifica que o valor k para busca de similaridade é 10.

        Cenário: Validação da configuração do sistema.
        Esperado: SIMILARITY_K == 10 (requisito do desafio MBA).
        """
        assert SIMILARITY_K == 10
