"""PDF ingestion module for RAG system.

This module handles loading PDF documents, splitting them into chunks,
generating embeddings, and storing them in PostgreSQL with pgVector.
"""

import os
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_pdf(path: str) -> List[Document]:
    """Load a PDF file and return its documents.

    Args:
        path: Path to the PDF file.

    Returns:
        List of Document objects from the PDF.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {path}")

    loader = PyPDFLoader(path)
    documents = loader.load()
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks using RecursiveCharacterTextSplitter.

    Args:
        documents: List of Document objects to split.

    Returns:
        List of chunked Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def get_embeddings() -> OpenAIEmbeddings:
    """Create and return OpenAI embeddings instance.

    Returns:
        OpenAIEmbeddings instance configured with text-embedding-3-small.
    """
    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )


def store_embeddings(chunks: List[Document], embeddings: OpenAIEmbeddings) -> PGVector:
    """Store document chunks with their embeddings in PGVector.

    Args:
        chunks: List of Document chunks to store.
        embeddings: OpenAIEmbeddings instance for generating vectors.

    Returns:
        PGVector instance with stored documents.

    Raises:
        ConnectionError: If database connection fails.
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
    """Main ingestion pipeline: load PDF, split, embed, and store.

    Returns:
        Number of chunks processed and stored.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the PDF contains no extractable text.
        ConnectionError: If database connection fails.
    """
    documents = load_pdf(PDF_PATH)

    if not documents:
        raise ValueError("PDF não contém texto extraível.")

    chunks = split_documents(documents)

    if not chunks:
        print("Aviso: Nenhum conteúdo de texto encontrado para indexar.")
        return 0

    embeddings = get_embeddings()
    store_embeddings(chunks, embeddings)

    return len(chunks)


if __name__ == "__main__":
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
