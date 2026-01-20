# Data Model: RAG Semantic Search System

**Feature**: 001-rag-semantic-search
**Date**: 2026-01-20
**Status**: Complete

## Overview

This document defines the data entities and their relationships for the RAG system. The primary storage is PostgreSQL with pgVector extension, managed through langchain-postgres PGVector abstraction.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         PDF Document                             │
│                      (document.pdf)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ PyPDFLoader.load()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangChain Document                          │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐   │
│  │   page_content  │  │            metadata                  │   │
│  │    (string)     │  │  {source: str, page: int}           │   │
│  └─────────────────┘  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ RecursiveCharacterTextSplitter.split()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Document Chunk                              │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐   │
│  │   page_content  │  │            metadata                  │   │
│  │  (≤1000 chars)  │  │  {source, page, chunk_index}        │   │
│  └─────────────────┘  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ OpenAIEmbeddings.embed()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    pgVector Collection                           │
│           (table: langchain_pg_embedding)                        │
│  ┌─────────┬────────────┬───────────┬─────────────────────────┐ │
│  │   id    │  document  │ embedding │       cmetadata         │ │
│  │  (uuid) │  (text)    │ (vector)  │        (jsonb)          │ │
│  └─────────┴────────────┴───────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entities

### 1. PDF Document (Source)

**Description**: The original PDF file containing text to be indexed.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| path | string | File system path to PDF | Must exist, readable |
| content | binary | PDF file content | Valid PDF format |

**Notes**:
- Single document per ingestion run
- Path configured via `PDF_PATH` environment variable
- Default: `document.pdf` in project root

---

### 2. LangChain Document (Intermediate)

**Description**: In-memory representation of PDF pages after loading.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| page_content | string | Text content of the page | Non-empty for valid pages |
| metadata.source | string | Original file path | Required |
| metadata.page | integer | Page number (0-indexed) | >= 0 |

**Notes**:
- Created by `PyPDFLoader.load()`
- Temporary, not persisted
- One Document per PDF page

---

### 3. Document Chunk (Intermediate)

**Description**: Text segment created from splitting documents.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| page_content | string | Chunk text content | ≤1000 characters |
| metadata.source | string | Original file path | Inherited |
| metadata.page | integer | Source page number | Inherited |
| metadata.chunk_index | integer | Position in split sequence | Auto-generated |

**Configuration**:
- `chunk_size`: 1000 characters (mandated)
- `chunk_overlap`: 150 characters (mandated)
- `separators`: ["\n\n", "\n", " ", ""]

**Notes**:
- Created by `RecursiveCharacterTextSplitter.split_documents()`
- Overlap ensures context continuity
- Multiple chunks per page possible

---

### 4. Embedding Vector (Stored)

**Description**: Numerical representation of chunk for similarity search.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| id | uuid | Unique identifier | Auto-generated |
| document | text | Original chunk text | From page_content |
| embedding | vector(1536) | OpenAI embedding | 1536 dimensions |
| cmetadata | jsonb | Chunk metadata | From metadata dict |

**Storage**: PostgreSQL table `langchain_pg_embedding`

**Index**: pgVector HNSW or IVFFlat for similarity search

---

### 5. User Query (Runtime)

**Description**: Question input by user via CLI.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| text | string | User's question | Non-empty |
| embedding | vector(1536) | Query embedding | Same model as docs |

**Notes**:
- Not persisted
- Converted to embedding for similarity search
- UTF-8 encoded for Portuguese support

---

### 6. Search Result (Runtime)

**Description**: Chunk returned from similarity search with relevance score.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| document | Document | Matching chunk | From vector store |
| score | float | Similarity score | 0.0 to 1.0 (cosine) |

**Configuration**:
- `k`: 10 results (mandated)
- Lower score = more similar (distance)

---

### 7. Context (Runtime)

**Description**: Concatenated text from top-k search results.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| text | string | Combined chunk texts | From k=10 results |
| chunks | list[Document] | Source chunks | Ordered by relevance |

**Notes**:
- Passed to LLM in prompt
- Separator: "\n\n" between chunks

---

### 8. Response (Runtime)

**Description**: LLM-generated answer to user query.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| text | string | Answer text | Context-based only |
| format | string | Display format | "RESPOSTA: {text}" |

**Validation**:
- Must not contain external knowledge
- Out-of-context: "Não tenho informações necessárias para responder sua pergunta."

---

## Database Schema

### PostgreSQL with pgVector

```sql
-- Extension (created by bootstrap service)
CREATE EXTENSION IF NOT EXISTS vector;

-- Main collection table (created by langchain-postgres)
CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    cmetadata JSONB
);

-- Embedding table (created by langchain-postgres)
CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
    document TEXT,
    embedding VECTOR(1536),
    cmetadata JSONB
);

-- Index for similarity search
CREATE INDEX IF NOT EXISTS langchain_pg_embedding_embedding_idx
ON langchain_pg_embedding
USING hnsw (embedding vector_cosine_ops);
```

**Notes**:
- Tables auto-created by `langchain-postgres` PGVector
- Index type: HNSW (Hierarchical Navigable Small World) for fast approximate search
- Collection name from `PG_VECTOR_COLLECTION_NAME` env var

---

## Data Flow

### Ingestion Pipeline

```
1. Load PDF
   PyPDFLoader(pdf_path).load() → List[Document]

2. Split into chunks
   RecursiveCharacterTextSplitter.split_documents(docs) → List[Document]

3. Generate embeddings & store
   PGVector.from_documents(chunks, embeddings) → VectorStore
```

### Query Pipeline

```
1. Receive question
   input() → str

2. Search similar chunks
   vector_store.similarity_search_with_score(question, k=10) → List[(Document, float)]

3. Build context
   "\n\n".join([doc.page_content for doc, score in results]) → str

4. Generate response
   llm.invoke(prompt.format(contexto=context, pergunta=question)) → str

5. Display
   print(f"RESPOSTA: {response}")
```

---

## Validation Rules

| Entity | Rule | Error Handling |
|--------|------|----------------|
| PDF Document | Must exist and be readable | FileNotFoundError message |
| PDF Document | Must contain extractable text | Warning if empty |
| Document Chunk | Must be ≤1000 characters | Enforced by splitter |
| User Query | Must be non-empty | Prompt to re-enter |
| Response | Must be context-based | Enforced by prompt template |

---

## State Transitions

### Document Processing States

```
[PDF File] --load--> [Raw Documents] --split--> [Chunks] --embed--> [Stored Vectors]
```

### Query Processing States

```
[User Input] --validate--> [Query] --embed--> [Search] --retrieve--> [Context] --generate--> [Response]
```
