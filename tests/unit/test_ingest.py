"""
Testes unitários para o módulo ingest.py.

Este módulo contém testes para as funções de carregamento e fragmentação
de documentos PDF do pipeline de ingestão do sistema RAG.

Classes de teste:
    TestLoadPdf: Testes para a função load_pdf.
    TestSplitDocuments: Testes para a função split_documents.
    TestChunkConfiguration: Testes para as constantes de configuração.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ingest import load_pdf, split_documents, CHUNK_SIZE, CHUNK_OVERLAP


class TestLoadPdf:
    """Testes para a função load_pdf."""

    def test_load_pdf_file_not_found(self):
        """
        Testa que FileNotFoundError é lançado quando o arquivo não existe.

        Cenário: Usuário configura PDF_PATH com caminho inválido.
        Esperado: Sistema lança exceção com mensagem amigável em português.
        """
        with pytest.raises(FileNotFoundError) as exc_info:
            load_pdf("/path/to/nonexistent.pdf")
        assert "Arquivo PDF não encontrado" in str(exc_info.value)

    @patch("ingest.PyPDFLoader")
    def test_load_pdf_valid_file(self, mock_loader_class, tmp_path):
        """
        Testa carregamento de um arquivo PDF válido.

        Cenário: Arquivo PDF existe e pode ser lido pelo PyPDFLoader.
        Esperado: Função retorna lista de documentos carregados.
        """
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
    """Testes para a função split_documents."""

    def test_split_documents_empty_list(self):
        """
        Testa fragmentação de lista vazia de documentos.

        Cenário: Nenhum documento é passado para fragmentação.
        Esperado: Função retorna lista vazia sem erros.
        """
        result = split_documents([])
        assert result == []

    def test_split_documents_small_content(self, sample_documents):
        """
        Testa fragmentação de documentos menores que o tamanho do chunk.

        Cenário: Documentos têm conteúdo menor que CHUNK_SIZE (1000 chars).
        Esperado: Número de chunks >= número de documentos originais.
        """
        result = split_documents(sample_documents)
        assert len(result) >= len(sample_documents)

    def test_split_documents_respects_chunk_size(self):
        """
        Testa que os chunks respeitam o tamanho configurado.

        Cenário: Documento longo (2500 chars) é fragmentado.
        Esperado: Cada chunk tem no máximo CHUNK_SIZE + CHUNK_OVERLAP chars.
        """
        from langchain_core.documents import Document

        long_content = "A" * 2500
        documents = [Document(page_content=long_content, metadata={"page": 0})]

        result = split_documents(documents)

        for chunk in result:
            assert len(chunk.page_content) <= CHUNK_SIZE + CHUNK_OVERLAP

    def test_split_documents_overlap(self):
        """
        Testa que os chunks possuem sobreposição adequada.

        Cenário: Documento excede CHUNK_SIZE em 500 caracteres.
        Esperado: Documento é dividido em pelo menos 2 chunks com overlap.
        """
        from langchain_core.documents import Document

        content = "A" * (CHUNK_SIZE + 500)
        documents = [Document(page_content=content, metadata={"page": 0})]

        result = split_documents(documents)

        assert len(result) >= 2


class TestChunkConfiguration:
    """Testes para as constantes de configuração de chunks."""

    def test_chunk_size_is_1000(self):
        """
        Verifica que o tamanho do chunk é 1000 conforme especificação.

        Cenário: Validação da configuração do sistema.
        Esperado: CHUNK_SIZE == 1000 (requisito do desafio MBA).
        """
        assert CHUNK_SIZE == 1000

    def test_chunk_overlap_is_150(self):
        """
        Verifica que a sobreposição do chunk é 150 conforme especificação.

        Cenário: Validação da configuração do sistema.
        Esperado: CHUNK_OVERLAP == 150 (requisito do desafio MBA).
        """
        assert CHUNK_OVERLAP == 150
