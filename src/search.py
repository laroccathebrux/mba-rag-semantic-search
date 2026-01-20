"""Search module for RAG system.

This module handles semantic search, prompt formatting, and LLM interactions
for the question-answering functionality.
"""

import os
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

SIMILARITY_K = 10

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def get_embeddings() -> OpenAIEmbeddings:
    """Create and return OpenAI embeddings instance.

    Returns:
        OpenAIEmbeddings instance configured with text-embedding-3-small.
    """
    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )


def get_vector_store() -> PGVector:
    """Initialize and return the vector store connection.

    Returns:
        PGVector instance connected to the database.

    Raises:
        ConnectionError: If database connection fails.
    """
    try:
        embeddings = get_embeddings()
        vector_store = PGVector(
            embeddings=embeddings,
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


def get_llm() -> ChatOpenAI:
    """Create and return ChatOpenAI instance.

    Returns:
        ChatOpenAI instance configured with gpt-5-nano and temperature=0.
    """
    return ChatOpenAI(
        model="gpt-5-nano",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )


def search_similar(
    vector_store: PGVector, query: str
) -> List[Tuple[Document, float]]:
    """Search for similar documents in the vector store.

    Args:
        vector_store: PGVector instance to search in.
        query: User question to search for.

    Returns:
        List of (Document, score) tuples, ordered by relevance.
    """
    results = vector_store.similarity_search_with_score(query, k=SIMILARITY_K)
    return results


def build_context(results: List[Tuple[Document, float]]) -> str:
    """Build context string from search results.

    Args:
        results: List of (Document, score) tuples from similarity search.

    Returns:
        Concatenated text from documents, separated by double newlines.
    """
    context_parts = [doc.page_content for doc, _ in results]
    return "\n\n".join(context_parts)


def format_prompt(contexto: str, pergunta: str) -> str:
    """Format the prompt template with context and question.

    Args:
        contexto: Retrieved context from similar documents.
        pergunta: User question.

    Returns:
        Formatted prompt string.
    """
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["contexto", "pergunta"],
    )
    return prompt.format(contexto=contexto, pergunta=pergunta)


def search_prompt(question: Optional[str] = None) -> Optional[str]:
    """Main search function: creates chain and optionally executes query.

    Args:
        question: User question to answer. If None, returns True to indicate
                  successful initialization.

    Returns:
        LLM response string when question is provided.
        True when question is None (indicates successful init).
        None if initialization fails.
    """
    try:
        vector_store = get_vector_store()
        llm = get_llm()

        if question is None:
            return True

        if not question.strip():
            return None

        results = search_similar(vector_store, question)
        context = build_context(results)
        formatted_prompt = format_prompt(context, question)

        response = llm.invoke(formatted_prompt)
        return response.content

    except ConnectionError as e:
        print(f"Erro: {e}")
        return None
    except Exception as e:
        print(f"Erro ao comunicar com serviço externo. Tente novamente. ({e})")
        return None
