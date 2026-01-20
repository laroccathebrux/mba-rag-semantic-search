# Internal API Contracts: RAG Semantic Search System

**Feature**: 001-rag-semantic-search
**Date**: 2026-01-20
**Status**: Complete

## Overview

This document defines the internal contracts between the three main modules (`ingest.py`, `search.py`, `chat.py`). Since this is a CLI application without external API endpoints, contracts focus on function signatures and data exchange formats.

---

## Module: ingest.py

### Purpose
PDF ingestion and vector storage

### Public Functions

#### `ingest_pdf() -> int`

Loads a PDF, splits into chunks, generates embeddings, and stores in pgVector.

**Parameters**: None (uses environment variables)

**Returns**: `int` - Number of chunks processed

**Environment Dependencies**:
- `PDF_PATH`: Path to PDF file
- `DATABASE_URL`: PostgreSQL connection string
- `PG_VECTOR_COLLECTION_NAME`: Collection name for vectors
- `OPENAI_API_KEY`: OpenAI API key

**Raises**:
- `FileNotFoundError`: PDF file not found
- `ValueError`: PDF contains no extractable text
- `ConnectionError`: Database connection failed
- `APIError`: OpenAI API call failed

**Example**:
```python
from ingest import ingest_pdf

try:
    count = ingest_pdf()
    print(f"Ingestão concluída: {count} chunks processados")
except FileNotFoundError as e:
    print(f"Erro: {e}")
```

**Contract**:
```
PRE:
  - PDF_PATH environment variable is set
  - File at PDF_PATH exists and is readable
  - DATABASE_URL points to running PostgreSQL with pgVector
  - OPENAI_API_KEY is valid

POST:
  - Database contains embeddings for all text chunks
  - Each chunk ≤1000 characters
  - Overlap of 150 characters between consecutive chunks
  - Returns count of chunks stored

INVARIANT:
  - Existing data in collection is preserved (append-only)
```

---

## Module: search.py

### Purpose
Search logic and prompt template management

### Public Constants

#### `PROMPT_TEMPLATE: str`

The prompt template for LLM queries (from challenge specification).

**Value**:
```python
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
```

### Public Functions

#### `search_prompt(question: str | None = None) -> str | None`

Creates a search chain and optionally executes a query.

**Parameters**:
- `question` (str | None): User question to answer. If None, returns initialized chain.

**Returns**:
- `str`: LLM response when question provided
- `None`: If initialization fails

**Environment Dependencies**:
- `DATABASE_URL`: PostgreSQL connection string
- `PG_VECTOR_COLLECTION_NAME`: Collection name
- `OPENAI_API_KEY`: OpenAI API key

**Raises**:
- `ConnectionError`: Database connection failed
- `APIError`: OpenAI API call failed

**Contract**:
```
PRE:
  - Database contains ingested embeddings
  - Environment variables configured
  - question is non-empty string (if provided)

POST:
  - Returns LLM-generated response based on context
  - Response is one of:
    a) Answer derived from document context
    b) "Não tenho informações necessárias para responder sua pergunta."
  - Never returns fabricated information

INVARIANT:
  - k=10 for similarity search
  - Uses gpt-5-nano model
  - Uses text-embedding-3-small for query embedding
```

---

#### `get_vector_store() -> PGVector`

Initializes and returns the vector store connection.

**Parameters**: None

**Returns**: `PGVector` - Connected vector store instance

**Contract**:
```
PRE:
  - DATABASE_URL is valid PostgreSQL connection string
  - PG_VECTOR_COLLECTION_NAME is set
  - OPENAI_API_KEY is valid

POST:
  - Returns connected PGVector instance
  - Connection is pooled and reusable
```

---

#### `build_context(results: list[tuple[Document, float]]) -> str`

Builds context string from search results.

**Parameters**:
- `results`: List of (Document, score) tuples from similarity search

**Returns**: `str` - Concatenated text from documents

**Contract**:
```
PRE:
  - results is list of (Document, float) tuples
  - Each Document has page_content attribute

POST:
  - Returns string with chunks separated by "\n\n"
  - Order matches input order (by relevance)
```

---

## Module: chat.py

### Purpose
CLI interface for user interaction

### Public Functions

#### `main() -> None`

Entry point for CLI chat application.

**Parameters**: None

**Returns**: None

**Behavior**:
1. Displays prompt "Faça sua pergunta:"
2. Accepts user input
3. Calls `search_prompt(question)` for each question
4. Displays "RESPOSTA: {answer}"
5. Loops until user exits

**Exit Conditions**:
- User types "sair", "exit", or "quit"
- Keyboard interrupt (Ctrl+C)

**Contract**:
```
PRE:
  - search module is importable
  - Database is accessible
  - OpenAI API is accessible

POST:
  - User sees prompt for input
  - Each question receives a response
  - Session can continue until explicit exit

INVARIANT:
  - Output format: "RESPOSTA: {answer}"
  - Empty input is ignored (re-prompt)
  - Encoding: UTF-8
```

---

## Data Exchange Formats

### Between ingest.py and search.py

**Shared**: PostgreSQL database with pgVector

| Field | Type | Description |
|-------|------|-------------|
| collection_name | string | From `PG_VECTOR_COLLECTION_NAME` |
| embedding_dimension | int | 1536 (text-embedding-3-small) |
| document_text | string | Chunk content (≤1000 chars) |
| metadata | jsonb | {source, page, chunk_index} |

### Between search.py and chat.py

**Function Call**: `search_prompt(question: str) -> str`

| Direction | Type | Description |
|-----------|------|-------------|
| Input | string | User question (UTF-8) |
| Output | string | LLM response |

---

## Error Handling Contract

All modules MUST follow this error handling pattern:

```python
class RAGError(Exception):
    """Base exception for RAG system"""
    pass

class ConfigurationError(RAGError):
    """Missing or invalid configuration"""
    pass

class DatabaseError(RAGError):
    """Database connection or query error"""
    pass

class ExternalServiceError(RAGError):
    """OpenAI API or external service error"""
    pass
```

**User-Facing Messages**:

| Exception | User Message |
|-----------|--------------|
| FileNotFoundError | "Arquivo PDF não encontrado: {path}" |
| ConfigurationError | "Configuração inválida: {detail}" |
| DatabaseError | "Erro ao conectar ao banco de dados. Verifique se está rodando." |
| ExternalServiceError | "Erro ao comunicar com serviço externo. Tente novamente." |

---

## Testing Contracts

### Unit Test Expectations

| Module | Function | Test Coverage |
|--------|----------|---------------|
| ingest.py | ingest_pdf | File loading, chunking, embedding call, DB storage |
| search.py | search_prompt | Query embedding, similarity search, prompt formatting |
| search.py | build_context | Context concatenation |
| chat.py | main | Input handling, output formatting |

### Mock Requirements

| External Dependency | Mock Strategy |
|---------------------|---------------|
| OpenAI Embeddings | Return fixed 1536-dim vector |
| OpenAI Chat | Return predetermined response |
| PostgreSQL | Use test database or mock PGVector |
| File System | Use tempfile or fixture PDF |
