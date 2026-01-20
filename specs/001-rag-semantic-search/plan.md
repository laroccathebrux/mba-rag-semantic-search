# Implementation Plan: RAG Semantic Search System

**Branch**: `001-rag-semantic-search` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-semantic-search/spec.md`

## Summary

Implement a RAG (Retrieval-Augmented Generation) system that ingests PDF documents into a PostgreSQL/pgVector database and provides a CLI interface for semantic question answering. The system uses LangChain for orchestration, OpenAI for embeddings (text-embedding-3-small) and LLM responses (gpt-5-nano), with strict context-only answers.

## Technical Context

**Language/Version**: Python 3.x (required by MBA challenge)
**Primary Dependencies**: LangChain (langchain, langchain-core, langchain-community, langchain-openai, langchain-postgres, langchain-text-splitters), pypdf
**Storage**: PostgreSQL 17 with pgVector extension (Docker)
**Testing**: pytest with mocks for external services
**Target Platform**: Local development (macOS/Linux with Docker)
**Project Type**: Single project (CLI application)
**Performance Goals**: Query response <5 seconds, ingestion proportional to document size
**Constraints**: k=10 for similarity search, 1000 char chunks with 150 overlap, context-only responses
**Scale/Scope**: Single PDF document, single user CLI interaction

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality Standards - COMPLIANT

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Single Responsibility | PASS | `ingest.py` (ingestion), `search.py` (search logic), `chat.py` (CLI) |
| Clean Code | PASS | Small focused functions with meaningful names |
| No Magic Values | PASS | Config via environment variables (.env) |
| Error Handling | PASS | Try/except for DB, API, file operations |
| Dependency Injection | PASS | Connections injectable for testing |
| Type Hints | PASS | All functions with type annotations |

### II. Testing Standards - COMPLIANT

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Unit Tests | PASS | Tests for embedding, search, prompt construction |
| Integration Tests | PASS | Mocked OpenAI, test database |
| Contract Tests | PASS | CLI input/output behavior tests |
| Test Coverage | PASS | >80% on critical paths |
| Test Isolation | PASS | Mocks for external services |
| Test Naming | PASS | `test_<function>_<scenario>_<expected>` |

### III. User Experience Consistency - COMPLIANT

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Clear Prompts | PASS | "Faca sua pergunta:" prompt |
| Consistent Response Format | PASS | "RESPOSTA: <answer>" format |
| Graceful Degradation | PASS | Standard out-of-context message |
| No Fabrication | PASS | Prompt rules enforce context-only |
| Error Messages | PASS | User-friendly error messages |
| Encoding | PASS | UTF-8 for Portuguese support |

### IV. Performance Requirements - COMPLIANT

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Ingestion Time | PASS | Chunked processing |
| Query Latency | PASS | pgVector indexed search <2s |
| Memory Efficiency | PASS | Stream processing, no full doc in memory |
| Database Efficiency | PASS | pgVector HNSW/IVFFlat indexes |
| Connection Pooling | PASS | psycopg pool via langchain-postgres |
| Graceful Limits | PASS | Error handling for edge cases |

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-semantic-search/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
├── docker-compose.yml      # PostgreSQL + pgVector setup
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Local environment (gitignored)
├── document.pdf           # PDF to be ingested
├── README.md              # Execution instructions
└── src/
    ├── ingest.py          # PDF ingestion script
    ├── search.py          # Search logic with prompt template
    └── chat.py            # CLI interface
```

**Structure Decision**: Single project structure per MBA challenge specification. The mandatory structure defines exactly three source files in `src/` directory. No additional subdirectories (models/, services/, etc.) to maintain compliance with challenge requirements.

## Complexity Tracking

> No constitution violations. Structure follows mandatory challenge requirements.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Flat src/ structure | Required | MBA challenge mandates exact file structure |
| No separate tests/ | Acceptable | Tests can be added in tests/ without violating challenge |
| Single PDF support | Sufficient | Challenge scope is single document ingestion |
