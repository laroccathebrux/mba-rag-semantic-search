"""Unit tests for search.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from search import build_context, format_prompt, PROMPT_TEMPLATE, SIMILARITY_K


class TestBuildContext:
    """Tests for build_context function."""

    def test_build_context_empty_results(self):
        """Test building context from empty results."""
        result = build_context([])
        assert result == ""

    def test_build_context_single_document(self):
        """Test building context from a single document."""
        doc = Document(page_content="Test content")
        results = [(doc, 0.9)]

        result = build_context(results)

        assert result == "Test content"

    def test_build_context_multiple_documents(self, sample_search_results):
        """Test building context from multiple documents."""
        result = build_context(sample_search_results)

        assert "\n\n" in result
        for doc, _ in sample_search_results:
            assert doc.page_content in result

    def test_build_context_preserves_order(self):
        """Test that context preserves document order."""
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
    """Tests for format_prompt function."""

    def test_format_prompt_includes_context(self):
        """Test that formatted prompt includes context."""
        result = format_prompt("Test context", "Test question")
        assert "Test context" in result

    def test_format_prompt_includes_question(self):
        """Test that formatted prompt includes question."""
        result = format_prompt("Test context", "Test question")
        assert "Test question" in result

    def test_format_prompt_includes_rules(self):
        """Test that formatted prompt includes rules."""
        result = format_prompt("Context", "Question")
        assert "REGRAS:" in result
        assert "Responda somente com base no CONTEXTO" in result

    def test_format_prompt_includes_examples(self):
        """Test that formatted prompt includes out-of-context examples."""
        result = format_prompt("Context", "Question")
        assert "capital da França" in result
        assert "Você acha isso bom ou ruim" in result


class TestPromptTemplate:
    """Tests for PROMPT_TEMPLATE constant."""

    def test_prompt_template_has_contexto_placeholder(self):
        """Test that template has {contexto} placeholder."""
        assert "{contexto}" in PROMPT_TEMPLATE

    def test_prompt_template_has_pergunta_placeholder(self):
        """Test that template has {pergunta} placeholder."""
        assert "{pergunta}" in PROMPT_TEMPLATE

    def test_prompt_template_has_no_info_response(self):
        """Test that template includes the standard 'no information' response."""
        assert "Não tenho informações necessárias para responder sua pergunta" in PROMPT_TEMPLATE

    def test_prompt_template_has_three_examples(self):
        """Test that template has exactly three out-of-context examples."""
        examples = PROMPT_TEMPLATE.count("Resposta: \"Não tenho informações")
        assert examples == 3


class TestConfiguration:
    """Tests for search configuration constants."""

    def test_similarity_k_is_10(self):
        """Verify k value for similarity search is 10 as per specification."""
        assert SIMILARITY_K == 10
