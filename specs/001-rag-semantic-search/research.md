# Research: RAG Semantic Search System

**Feature**: 001-rag-semantic-search
**Date**: 2026-01-20
**Status**: Complete

## Overview

This document consolidates technical research and decisions for implementing the RAG system per MBA challenge requirements. All technology choices are mandated by the challenge specification (intro.md).

---

## 1. PDF Processing

### Decision: PyPDFLoader from langchain-community

**Rationale**:
- Mandated by challenge specification
- Native LangChain integration
- Returns Document objects compatible with text splitters

**Implementation**:
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(pdf_path)
documents = loader.load()
```

**Alternatives Considered**:
- `pdfplumber`: More control but not LangChain-native
- `PyMuPDF (fitz)`: Faster but requires additional integration
- **Rejected**: Challenge mandates PyPDFLoader

---

## 2. Text Chunking

### Decision: RecursiveCharacterTextSplitter with 1000/150 params

**Rationale**:
- Mandated by challenge: 1000 characters, 150 overlap
- RecursiveCharacterTextSplitter preserves semantic boundaries
- Overlap ensures context continuity across chunks

**Implementation**:
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(documents)
```

**Alternatives Considered**:
- `CharacterTextSplitter`: Simpler but doesn't respect boundaries
- `TokenTextSplitter`: Token-based but challenge specifies characters
- **Rejected**: Challenge mandates character-based chunking

---

## 3. Embedding Model

### Decision: OpenAI text-embedding-3-small

**Rationale**:
- Mandated by challenge specification
- 1536-dimensional vectors
- Cost-effective for educational project
- Excellent multilingual (Portuguese) support

**Implementation**:
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

**Alternatives Considered**:
- `text-embedding-3-large`: Higher quality but more expensive
- `Google embedding-001`: Supported but OpenAI is primary
- **Rejected**: Challenge mandates text-embedding-3-small

---

## 4. Vector Storage

### Decision: PostgreSQL with pgVector via langchain-postgres

**Rationale**:
- Mandated by challenge specification
- PGVector provides efficient similarity search
- langchain-postgres offers seamless integration
- Docker Compose provided for easy setup

**Implementation**:
```python
from langchain_postgres import PGVector

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
    connection=os.getenv("DATABASE_URL"),
    use_jsonb=True
)
```

**Database Configuration**:
- Image: `pgvector/pgvector:pg17`
- Database: `rag`
- User/Password: `postgres/postgres`
- Port: 5432

**Alternatives Considered**:
- `Chroma`: Simpler but not PostgreSQL
- `Pinecone`: Cloud-hosted, not local
- `FAISS`: In-memory only
- **Rejected**: Challenge mandates PostgreSQL + pgVector

---

## 5. Similarity Search

### Decision: similarity_search_with_score with k=10

**Rationale**:
- Mandated by challenge: k=10 results
- Score provides relevance ranking
- Sufficient context for LLM without overwhelming

**Implementation**:
```python
results = vector_store.similarity_search_with_score(
    query=user_question,
    k=10
)
context = "\n\n".join([doc.page_content for doc, score in results])
```

**Alternatives Considered**:
- `similarity_search`: No scores, less debugging info
- `max_marginal_relevance_search`: Diversity-focused
- **Rejected**: Challenge mandates standard similarity search

---

## 6. LLM for Response Generation

### Decision: OpenAI gpt-5-nano via langchain-openai

**Rationale**:
- Mandated by challenge specification
- Cost-effective for Q&A tasks
- Follows instructions well (context-only responses)

**Implementation**:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

**Alternatives Considered**:
- `gpt-4`: More capable but expensive
- `gpt-3.5-turbo`: Good balance but not specified
- **Rejected**: Challenge mandates gpt-5-nano

---

## 7. Prompt Engineering

### Decision: Strict context-only prompt template

**Rationale**:
- Challenge provides exact prompt template
- Includes examples of out-of-context responses
- Enforces no fabrication rule

**Implementation**:
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

---

## 8. Environment Configuration

### Decision: python-dotenv with .env file

**Rationale**:
- Standard Python practice
- Keeps secrets out of code
- Easy local development

**Required Variables**:
```env
OPENAI_API_KEY=<your-key>
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

---

## 9. CLI Implementation

### Decision: Simple input() loop in chat.py

**Rationale**:
- Challenge requires terminal-based chat
- No need for complex CLI frameworks
- Direct user interaction pattern

**Implementation Pattern**:
```python
def main():
    print("Faça sua pergunta:")
    while True:
        question = input("\nPERGUNTA: ").strip()
        if not question:
            continue
        if question.lower() in ['sair', 'exit', 'quit']:
            break
        response = search_and_respond(question)
        print(f"RESPOSTA: {response}")
```

---

## 10. Error Handling Strategy

### Decision: User-friendly error messages with logging

**Rationale**:
- Constitution requires user-friendly errors
- Logging for debugging without exposing details

**Error Categories**:

| Error Type | User Message | Log Level |
|------------|--------------|-----------|
| File not found | "Arquivo PDF não encontrado: {path}" | ERROR |
| DB connection | "Erro ao conectar ao banco de dados. Verifique se está rodando." | ERROR |
| API error | "Erro ao comunicar com serviço externo. Tente novamente." | ERROR |
| Empty PDF | "PDF não contém texto extraível." | WARNING |
| Empty question | "Por favor, digite uma pergunta válida." | INFO |

---

## Summary of Decisions

| Component | Technology | Source |
|-----------|------------|--------|
| PDF Loading | PyPDFLoader | Mandated |
| Text Splitting | RecursiveCharacterTextSplitter (1000/150) | Mandated |
| Embeddings | OpenAI text-embedding-3-small | Mandated |
| Vector Store | PostgreSQL + pgVector | Mandated |
| Similarity Search | k=10 | Mandated |
| LLM | OpenAI gpt-5-nano | Mandated |
| Prompt | Challenge-provided template | Mandated |
| Config | python-dotenv | Best practice |
| CLI | Standard input/print | Sufficient |

All NEEDS CLARIFICATION items resolved - all technology choices are mandated by MBA challenge specification.
