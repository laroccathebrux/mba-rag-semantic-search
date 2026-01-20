<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change: N/A → 1.0.0 (Initial constitution)

Added Principles:
- I. Code Quality Standards
- II. Testing Standards
- III. User Experience Consistency
- IV. Performance Requirements

Added Sections:
- Technology Constraints (mandatory stack and packages)
- Development Workflow (code review, quality gates)
- Governance (amendment procedures, versioning)

Templates Status:
- .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
- .specify/templates/spec-template.md: ✅ Compatible (Success Criteria aligns with performance principles)
- .specify/templates/tasks-template.md: ✅ Compatible (Test-first approach supported)
- .specify/templates/commands/*.md: N/A (no command files found)

Follow-up TODOs: None
================================================================================
-->

# RAG System Constitution

## Core Principles

### I. Code Quality Standards

All code in this project MUST adhere to the following non-negotiable standards:

- **Single Responsibility**: Each module (`ingest.py`, `search.py`, `chat.py`) MUST have one clear purpose
- **Clean Code**: Functions MUST be small, focused, and self-documenting with meaningful names
- **No Magic Values**: All configuration (chunk sizes, overlap, k-value) MUST be externalized to environment variables or constants
- **Error Handling**: All external operations (database connections, API calls, file reads) MUST have explicit error handling with meaningful error messages
- **Dependency Injection**: Database connections and API clients SHOULD be injectable for testability
- **Type Hints**: All function signatures MUST include type hints for parameters and return values

**Rationale**: A RAG system handles sensitive document data and user queries. Code quality ensures maintainability, debuggability, and reduces the risk of silent failures in production.

### II. Testing Standards

Testing is mandatory for ensuring system reliability:

- **Unit Tests**: Each service function (embedding generation, similarity search, prompt construction) MUST have unit tests
- **Integration Tests**: Database operations and LLM calls MUST have integration tests with mocked external services
- **Contract Tests**: The CLI interface MUST be tested for expected input/output behavior
- **Test Coverage**: Critical paths (ingestion pipeline, query pipeline) MUST have >80% coverage
- **Test Isolation**: Tests MUST NOT depend on external services (use mocks for OpenAI, test database for PostgreSQL)
- **Test Naming**: Tests MUST follow the pattern `test_<function>_<scenario>_<expected_result>`

**Rationale**: The system processes user queries against document content. Incorrect responses or silent failures directly impact user trust and system reliability.

### III. User Experience Consistency

The CLI interface MUST provide a consistent and predictable user experience:

- **Clear Prompts**: User-facing prompts MUST be explicit (e.g., "Faça sua pergunta:")
- **Consistent Response Format**: All responses MUST follow the pattern `RESPOSTA: <answer>`
- **Graceful Degradation**: Out-of-context questions MUST return exactly: "Não tenho informações necessárias para responder sua pergunta."
- **No Fabrication**: Responses MUST NEVER include information not present in the document context
- **Error Messages**: System errors MUST be user-friendly, not raw stack traces
- **Encoding**: All text I/O MUST use UTF-8 to properly handle Portuguese characters

**Rationale**: Users interact with the system via CLI and expect consistent, predictable behavior. Inconsistent responses or cryptic errors erode user confidence.

### IV. Performance Requirements

The system MUST meet these performance baselines:

- **Ingestion Time**: PDF ingestion (1000 chars/chunk, 150 overlap) MUST complete within reasonable time proportional to document size
- **Query Latency**: Similarity search (k=10) MUST return results in <2 seconds for databases with <10,000 chunks
- **Memory Efficiency**: Embedding operations MUST NOT load entire document into memory; MUST process in chunks
- **Database Efficiency**: Vector similarity searches MUST use pgVector indexes, not full table scans
- **Connection Pooling**: Database connections MUST be pooled, not created per-query
- **Graceful Limits**: System MUST handle edge cases (empty PDF, very large documents) without crashing

**Rationale**: A slow or resource-intensive RAG system degrades user experience and increases operational costs.

## Technology Constraints

This project has mandatory technology requirements per the MBA challenge specification:

**Language & Framework**:
- Python 3.x (required)
- LangChain framework (required)

**Database**:
- PostgreSQL with pgVector extension (required)
- Docker & Docker Compose for database execution (required)

**Packages (Mandatory)**:
- `langchain`, `langchain-core`, `langchain-community`
- `langchain-openai` for embeddings and LLM
- `langchain-postgres` for PGVector integration
- `langchain-text-splitters` for RecursiveCharacterTextSplitter
- `pypdf` for PDF loading
- `psycopg` / `psycopg-binary` for PostgreSQL driver
- `python-dotenv` for environment variables

**Models (Mandatory)**:
- Embedding model: `text-embedding-3-small`
- LLM model: `gpt-5-nano`

**Configuration (Mandatory)**:
- Chunk size: 1000 characters
- Chunk overlap: 150 characters
- Similarity search: k=10

## Development Workflow

### Code Review Requirements

- All changes MUST be reviewed for adherence to the four core principles
- Database schema changes MUST be reviewed for index optimization
- Prompt template changes MUST be reviewed for instruction clarity

### Quality Gates

Before merging any code:

1. **Linting**: Code MUST pass `flake8` or equivalent linter
2. **Type Checking**: Code MUST pass `mypy` type checking
3. **Tests**: All tests MUST pass
4. **Manual Verification**: CLI interaction MUST be manually tested with sample queries

### Project Structure

The following structure is mandatory per specification:

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
├── document.pdf
└── README.md
```

## Governance

### Amendment Procedure

1. Amendments MUST be documented with clear rationale
2. Amendments affecting core principles require explicit justification
3. All amendments MUST update the version number per semantic versioning

### Versioning Policy

- **MAJOR**: Removing or fundamentally changing a core principle
- **MINOR**: Adding new principles or sections, material guidance expansion
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

### Compliance Review

- All PRs MUST verify compliance with this constitution
- Constitution violations MUST be documented in the Complexity Tracking section of the implementation plan
- Runtime development guidance is provided in `CLAUDE.md`

**Version**: 1.0.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20
