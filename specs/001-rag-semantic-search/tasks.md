# Tasks: RAG Semantic Search System

**Input**: Design documents from `/specs/001-rag-semantic-search/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests included per Constitution II Testing Standards (mandatory).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root per MBA challenge specification
- Mandatory structure: `src/ingest.py`, `src/search.py`, `src/chat.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [ ] T001 Verify docker-compose.yml exists and matches pgvector/pgvector:pg17 spec in docker-compose.yml
- [ ] T002 [P] Create .env.example with all required variables (OPENAI_API_KEY, DATABASE_URL, PG_VECTOR_COLLECTION_NAME, PDF_PATH) in .env.example
- [ ] T003 [P] Update requirements.txt with exact versions from reference codebase in requirements.txt
- [ ] T004 Create .gitignore with .env and __pycache__ entries in .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Start PostgreSQL with pgVector using docker compose up -d
- [ ] T006 Verify pgVector extension is enabled by checking bootstrap_vector_ext service logs
- [ ] T007 Create .env file from .env.example with actual OPENAI_API_KEY
- [ ] T008 [P] Install Python dependencies with pip install -r requirements.txt

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 2.5: Test Infrastructure (Constitution Requirement)

**Purpose**: Setup testing framework per Constitution II Testing Standards

- [ ] T008a [P] Create tests/ directory structure with tests/unit/, tests/integration/, tests/contract/
- [ ] T008b [P] Add pytest and pytest-mock to requirements.txt
- [ ] T008c [P] Create tests/conftest.py with shared fixtures (mock embeddings, mock LLM, test DB URL)

**Checkpoint**: Test infrastructure ready

---

## Phase 3: User Story 1 - PDF Ingestion (Priority: P1)

**Goal**: Ingest PDF document, split into chunks, generate embeddings, store in pgVector

**Independent Test**: Run `python src/ingest.py` with sample PDF, verify chunks stored in database

### Implementation for User Story 1

- [ ] T009 [US1] Import required modules (os, dotenv, PyPDFLoader, RecursiveCharacterTextSplitter, OpenAIEmbeddings, PGVector) in src/ingest.py
- [ ] T010 [US1] Load environment variables using load_dotenv() in src/ingest.py
- [ ] T011 [US1] Define configuration constants from environment (PDF_PATH, DATABASE_URL, PG_VECTOR_COLLECTION_NAME, chunk_size=1000, chunk_overlap=150) in src/ingest.py
- [ ] T012 [US1] Implement load_pdf() function using PyPDFLoader to load PDF and return documents in src/ingest.py
- [ ] T013 [US1] Implement split_documents() function using RecursiveCharacterTextSplitter with 1000/150 params in src/ingest.py
- [ ] T014 [US1] Implement get_embeddings() function returning OpenAIEmbeddings with text-embedding-3-small model in src/ingest.py
- [ ] T015 [US1] Implement store_embeddings() function using PGVector.from_documents() in src/ingest.py
- [ ] T016 [US1] Implement ingest_pdf() main function orchestrating load->split->embed->store pipeline in src/ingest.py
- [ ] T017 [US1] Add error handling for FileNotFoundError with user-friendly message in src/ingest.py
- [ ] T018 [US1] Add error handling for empty PDF (no text extracted) with warning message in src/ingest.py
- [ ] T019 [US1] Add error handling for database connection errors in src/ingest.py
- [ ] T020 [US1] Add error handling for OpenAI API errors in src/ingest.py
- [ ] T021 [US1] Add type hints to all functions in src/ingest.py
- [ ] T022 [US1] Add success message printing chunk count on completion in src/ingest.py
- [ ] T023 [US1] Add if __name__ == "__main__" block calling ingest_pdf() in src/ingest.py

### Tests for User Story 1

- [ ] T023a [P] [US1] Unit test for load_pdf() with valid/invalid paths in tests/unit/test_ingest.py
- [ ] T023b [P] [US1] Unit test for split_documents() verifying 1000/150 chunking in tests/unit/test_ingest.py
- [ ] T023c [P] [US1] Integration test for ingest_pdf() with mocked OpenAI in tests/integration/test_ingest.py

**Checkpoint**: User Story 1 complete - PDF ingestion works independently

**Validation**:
```bash
python src/ingest.py
# Expected: "Ingestao concluida: X chunks processados"
```

---

## Phase 4: User Story 2 - Semantic Question Answering (Priority: P2)

**Goal**: CLI interface for asking questions and receiving context-based answers

**Independent Test**: Run `python src/chat.py`, ask a question about PDF content, verify accurate response

### Implementation for User Story 2 - search.py

- [ ] T024 [US2] Import required modules (os, dotenv, PGVector, OpenAIEmbeddings, ChatOpenAI, PromptTemplate) in src/search.py
- [ ] T025 [US2] Load environment variables using load_dotenv() in src/search.py
- [ ] T026 [US2] Define PROMPT_TEMPLATE constant with exact template from challenge specification in src/search.py
- [ ] T027 [US2] Implement get_embeddings() function returning OpenAIEmbeddings with text-embedding-3-small in src/search.py
- [ ] T028 [US2] Implement get_vector_store() function returning PGVector instance connected to database in src/search.py
- [ ] T029 [US2] Implement get_llm() function returning ChatOpenAI with gpt-5-nano model and temperature=0 in src/search.py
- [ ] T030 [US2] Implement search_similar() function using similarity_search_with_score with k=10 in src/search.py
- [ ] T031 [US2] Implement build_context() function concatenating document page_content with "\n\n" separator in src/search.py
- [ ] T032 [US2] Implement format_prompt() function using PROMPT_TEMPLATE with contexto and pergunta variables in src/search.py
- [ ] T033 [US2] Implement search_prompt() function orchestrating search->context->prompt->llm pipeline in src/search.py
- [ ] T034 [US2] Add error handling for database connection errors in src/search.py
- [ ] T035 [US2] Add error handling for OpenAI API errors in src/search.py
- [ ] T036 [US2] Add type hints to all functions in src/search.py

### Implementation for User Story 2 - chat.py

- [ ] T037 [US2] Import search_prompt from search module in src/chat.py
- [ ] T038 [US2] Implement main() function with "Faca sua pergunta:" prompt in src/chat.py
- [ ] T039 [US2] Implement input loop accepting user questions in src/chat.py
- [ ] T040 [US2] Call search_prompt() for each non-empty question in src/chat.py
- [ ] T041 [US2] Display response with "RESPOSTA: {answer}" format in src/chat.py
- [ ] T042 [US2] Handle empty input by re-prompting without error in src/chat.py
- [ ] T043 [US2] Implement exit conditions for "sair", "exit", "quit" commands in src/chat.py
- [ ] T044 [US2] Handle KeyboardInterrupt (Ctrl+C) gracefully in src/chat.py
- [ ] T045 [US2] Add error handling displaying user-friendly messages in src/chat.py
- [ ] T046 [US2] Add type hints to all functions in src/chat.py
- [ ] T047 [US2] Add if __name__ == "__main__" block calling main() in src/chat.py

### Tests for User Story 2

- [ ] T047a [P] [US2] Unit test for build_context() in tests/unit/test_search.py
- [ ] T047b [P] [US2] Unit test for format_prompt() in tests/unit/test_search.py
- [ ] T047c [P] [US2] Integration test for search_prompt() with mocked OpenAI/DB in tests/integration/test_search.py
- [ ] T047d [P] [US2] Contract test for chat.py input/output format in tests/contract/test_chat.py

**Checkpoint**: User Story 2 complete - Q&A works independently

**Validation**:
```bash
python src/chat.py
# PERGUNTA: [question about PDF content]
# RESPOSTA: [accurate answer from document]
```

---

## Phase 5: User Story 3 - Out-of-Context Question Handling (Priority: P3)

**Goal**: Ensure questions outside document scope receive standard "information not available" response

**Independent Test**: Ask questions unrelated to PDF, verify exact response message

### Implementation for User Story 3

- [ ] T048 [US3] Verify PROMPT_TEMPLATE includes all three out-of-context examples in src/search.py
- [ ] T049 [US3] Verify PROMPT_TEMPLATE rule "Se a informação não estiver explicitamente no CONTEXTO" in src/search.py
- [ ] T050 [US3] Verify PROMPT_TEMPLATE rule "Nunca invente ou use conhecimento externo" in src/search.py
- [ ] T051 [US3] Verify PROMPT_TEMPLATE rule "Nunca produza opinioes ou interpretacoes" in src/search.py
- [ ] T052 [US3] Test with out-of-context question "Qual a capital da Franca?" and verify standard response
- [ ] T053 [US3] Test with opinion question "Voce acha isso bom ou ruim?" and verify standard response

**Checkpoint**: User Story 3 complete - Out-of-context handling verified

**Validation**:
```bash
python src/chat.py
# PERGUNTA: Qual a capital da Franca?
# RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation and validation

- [ ] T054 [P] Update README.md with execution instructions per quickstart.md
- [ ] T055 [P] Ensure UTF-8 encoding for Portuguese characters in all files
- [ ] T056 Run complete quickstart.md validation flow (docker up, ingest, chat)
- [ ] T057 Verify all error messages are user-friendly (no stack traces to user)
- [ ] T058 [P] Run flake8 linting on all src/ files and fix any violations
- [ ] T059 [P] Run mypy type checking on all src/ files and fix any type errors
- [ ] T060 Run pytest and verify all tests pass with >80% coverage on critical paths
- [ ] T061 Validate query response time <5 seconds with sample questions (SC-002)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - PDF ingestion
- **User Story 2 (Phase 4)**: Depends on Foundational AND User Story 1 (needs ingested data to query)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (tests Q&A behavior)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Foundational - can be MVP
- **User Story 2 (P2)**: Requires US1 data to be meaningful (but code can be written first)
- **User Story 3 (P3)**: Verification of US2 behavior - no new code, just validation

### Within Each User Story

- Configuration before functions
- Helper functions before main orchestration function
- Error handling integrated with each function
- Type hints added to each function as implemented

### Parallel Opportunities

**Phase 1 Setup**:
```bash
# These can run in parallel:
Task T002: ".env.example"
Task T003: "requirements.txt"
```

**Phase 2 Foundational**:
```bash
# T008 can run in parallel with T005-T007:
Task T008: "pip install -r requirements.txt"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (PDF Ingestion)
4. **STOP and VALIDATE**: Run `python src/ingest.py` with sample PDF
5. Verify chunks in database

### Incremental Delivery

1. Complete Setup + Foundational → Environment ready
2. Add User Story 1 → Test ingestion → **MVP: Can ingest PDFs**
3. Add User Story 2 → Test Q&A → **Full feature: Can ask questions**
4. Add User Story 3 → Verify behavior → **Production ready: Handles edge cases**

### Single Developer Strategy

Execute phases sequentially in priority order (P1 → P2 → P3). Stop at any checkpoint to validate.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each phase or logical group of tasks
- Stop at any checkpoint to validate functionality
- MBA challenge mandates exact file structure: src/ingest.py, src/search.py, src/chat.py
