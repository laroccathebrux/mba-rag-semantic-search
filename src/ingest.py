"""
Módulo de ingestão de PDF para o sistema RAG.

Este módulo é responsável pelo pipeline de ingestão de documentos PDF,
que inclui:
    1. Carregamento do arquivo PDF
    2. Divisão do texto em chunks (fragmentos)
    3. Geração de embeddings vetoriais
    4. Armazenamento no banco de dados PostgreSQL com pgVector

O pipeline segue a arquitetura RAG (Retrieval-Augmented Generation) onde
os documentos são primeiro processados e indexados para posterior recuperação
durante as consultas do usuário.

Configuração via variáveis de ambiente:
    - PDF_PATH: Caminho para o arquivo PDF a ser ingerido
    - DATABASE_URL: URL de conexão com PostgreSQL
    - PG_VECTOR_COLLECTION_NAME: Nome da coleção no pgVector
    - OPENAI_API_KEY: Chave de API da OpenAI
    - OPENAI_EMBEDDING_MODEL: Modelo de embeddings (default: text-embedding-3-small)

Exemplo de uso:
    $ python src/ingest.py
    Ingestão concluída: 42 chunks processados

Author: Alessandro Silveira
Date: 2026-01-20
"""

import os
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações carregadas do ambiente
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
"""str: Caminho para o arquivo PDF a ser processado."""

DATABASE_URL = os.getenv("DATABASE_URL")
"""str: URL de conexão com o banco de dados PostgreSQL."""

PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
"""str: Nome da coleção onde os vetores serão armazenados."""

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
"""str: Chave de API da OpenAI para geração de embeddings."""

OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
"""str: Modelo de embeddings da OpenAI a ser utilizado."""

# Configurações de chunking conforme especificação do desafio
CHUNK_SIZE = 1000
"""int: Tamanho máximo de cada chunk em caracteres."""

CHUNK_OVERLAP = 150
"""int: Sobreposição entre chunks consecutivos em caracteres."""


def load_pdf(path: str) -> List[Document]:
    """
    Carrega um arquivo PDF e retorna seu conteúdo como documentos.

    Utiliza o PyPDFLoader do LangChain para extrair o texto de cada página
    do PDF, preservando metadados como número da página.

    Args:
        path (str): Caminho absoluto ou relativo para o arquivo PDF.

    Returns:
        List[Document]: Lista de objetos Document do LangChain, onde cada
            documento representa uma página do PDF com seu conteúdo textual
            e metadados associados.

    Raises:
        FileNotFoundError: Se o arquivo PDF não existir no caminho especificado.

    Example:
        >>> documents = load_pdf("documento.pdf")
        >>> print(f"Carregadas {len(documents)} páginas")
        Carregadas 10 páginas
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {path}")

    loader = PyPDFLoader(path)
    documents = loader.load()
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Divide documentos em chunks menores usando RecursiveCharacterTextSplitter.

    Esta função implementa a estratégia de chunking definida na especificação:
    - Tamanho do chunk: 1000 caracteres
    - Sobreposição: 150 caracteres

    A sobreposição garante que o contexto não seja perdido nas bordas dos chunks,
    permitindo que informações que cruzam limites de chunk sejam capturadas.

    Args:
        documents (List[Document]): Lista de documentos do LangChain a serem
            divididos. Cada documento pode conter texto de qualquer tamanho.

    Returns:
        List[Document]: Lista de chunks (fragmentos) de documentos. Cada chunk
            mantém os metadados do documento original, acrescidos de informações
            sobre a posição do chunk.

    Note:
        O RecursiveCharacterTextSplitter tenta dividir o texto em pontos naturais
        (parágrafos, sentenças, palavras) antes de recorrer a divisões arbitrárias.

    Example:
        >>> chunks = split_documents(documents)
        >>> print(f"Documento dividido em {len(chunks)} chunks")
        Documento dividido em 42 chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def get_embeddings() -> OpenAIEmbeddings:
    """
    Cria e retorna uma instância de OpenAIEmbeddings.

    Configura o cliente de embeddings da OpenAI com o modelo especificado
    nas variáveis de ambiente. O modelo padrão é 'text-embedding-3-small',
    que gera vetores de 1536 dimensões.

    Returns:
        OpenAIEmbeddings: Instância configurada do cliente de embeddings
            pronta para gerar vetores a partir de texto.

    Note:
        O modelo text-embedding-3-small oferece um bom equilíbrio entre
        qualidade dos embeddings e custo de API.
    """
    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )


def store_embeddings(chunks: List[Document], embeddings: OpenAIEmbeddings) -> PGVector:
    """
    Armazena chunks de documentos com seus embeddings no PGVector.

    Esta função realiza as seguintes operações:
    1. Gera embeddings para cada chunk usando a API da OpenAI
    2. Conecta ao banco de dados PostgreSQL com extensão pgVector
    3. Armazena os chunks e seus vetores na coleção especificada

    Args:
        chunks (List[Document]): Lista de chunks de documentos a serem
            armazenados. Cada chunk deve ter page_content e metadata.
        embeddings (OpenAIEmbeddings): Instância do cliente de embeddings
            para geração dos vetores.

    Returns:
        PGVector: Instância do vector store conectada ao banco de dados,
            que pode ser usada para buscas por similaridade.

    Raises:
        ConnectionError: Se a conexão com o banco de dados falhar.
            Isso pode ocorrer se o PostgreSQL não estiver rodando ou
            se as credenciais estiverem incorretas.

    Note:
        Os embeddings são armazenados de forma persistente no PostgreSQL,
        permitindo que sejam consultados em execuções futuras sem necessidade
        de reprocessamento.
    """
    try:
        vector_store = PGVector.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=PG_VECTOR_COLLECTION_NAME,
            connection=DATABASE_URL,
        )
        return vector_store
    except Exception as e:
        if "connect" in str(e).lower() or "connection" in str(e).lower():
            raise ConnectionError(
                "Erro ao conectar ao banco de dados. Verifique se está rodando."
            ) from e
        raise


def ingest_pdf() -> int:
    """
    Pipeline principal de ingestão: carrega PDF, divide, gera embeddings e armazena.

    Esta é a função orquestradora que executa todo o pipeline de ingestão:
    1. Carrega o PDF do caminho configurado em PDF_PATH
    2. Valida se o PDF contém texto extraível
    3. Divide o conteúdo em chunks de 1000 caracteres com 150 de sobreposição
    4. Gera embeddings usando o modelo da OpenAI
    5. Armazena tudo no PostgreSQL com pgVector

    Returns:
        int: Número de chunks processados e armazenados com sucesso.
            Retorna 0 se o PDF não contiver texto para indexar.

    Raises:
        FileNotFoundError: Se o arquivo PDF não existir no caminho configurado.
        ValueError: Se o PDF não contiver texto extraível (ex: PDF de imagens).
        ConnectionError: Se a conexão com o banco de dados falhar.

    Example:
        >>> count = ingest_pdf()
        >>> print(f"Ingestão concluída: {count} chunks processados")
        Ingestão concluída: 42 chunks processados

    Note:
        Esta função deve ser executada uma vez para cada documento antes
        de usar o chat para fazer perguntas sobre seu conteúdo.
    """
    # Etapa 1: Carregar o PDF
    documents = load_pdf(PDF_PATH)

    # Etapa 2: Validar conteúdo
    if not documents:
        raise ValueError("PDF não contém texto extraível.")

    # Etapa 3: Dividir em chunks
    chunks = split_documents(documents)

    if not chunks:
        print("Aviso: Nenhum conteúdo de texto encontrado para indexar.")
        return 0

    # Etapa 4: Gerar embeddings e armazenar
    embeddings = get_embeddings()
    store_embeddings(chunks, embeddings)

    return len(chunks)


if __name__ == "__main__":
    """
    Ponto de entrada para execução via linha de comando.

    Executa o pipeline de ingestão e exibe mensagens apropriadas
    de sucesso ou erro para o usuário.
    """
    try:
        count = ingest_pdf()
        print(f"Ingestão concluída: {count} chunks processados")
    except FileNotFoundError as e:
        print(f"Erro: {e}")
    except ValueError as e:
        print(f"Erro: {e}")
    except ConnectionError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro ao comunicar com serviço externo. Tente novamente. ({e})")
