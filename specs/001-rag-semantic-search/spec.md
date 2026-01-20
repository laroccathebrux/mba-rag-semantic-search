# Feature Specification: RAG Semantic Search System

**Feature Branch**: `001-rag-semantic-search`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Implementar sistema RAG para ingestao de PDF e busca semantica via CLI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - PDF Ingestion (Priority: P1)

As a system administrator, I want to ingest a PDF document into the system so that its content becomes searchable through semantic queries.

**Why this priority**: Without ingestion, there is no data to search. This is the foundational capability that enables all other features.

**Independent Test**: Can be fully tested by running the ingestion script with a sample PDF and verifying that document chunks are stored in the database with their embeddings.

**Acceptance Scenarios**:

1. **Given** a PDF file exists at the configured path, **When** the ingestion script is executed, **Then** the PDF content is split into chunks of 1000 characters with 150 character overlap
2. **Given** the PDF has been split into chunks, **When** the ingestion process completes, **Then** each chunk has a corresponding embedding vector stored in the database
3. **Given** the database is running with pgVector extension, **When** ingestion completes successfully, **Then** the user sees a confirmation message indicating the number of chunks processed
4. **Given** the PDF file does not exist at the configured path, **When** the ingestion script is executed, **Then** the system displays a clear error message indicating the file was not found

---

### User Story 2 - Semantic Question Answering (Priority: P2)

As a user, I want to ask questions via command line and receive answers based solely on the ingested PDF content, so that I can quickly find information without reading the entire document.

**Why this priority**: This is the core user-facing feature that delivers value from the ingested data. Depends on P1 being complete.

**Independent Test**: Can be fully tested by starting the CLI chat, asking a question about content known to be in the PDF, and verifying the response contains accurate information from the document.

**Acceptance Scenarios**:

1. **Given** the PDF has been ingested, **When** the user asks a question about content in the document, **Then** the system returns an accurate answer based on the document context
2. **Given** the user asks a question, **When** the system processes the query, **Then** it retrieves the 10 most semantically similar chunks from the database
3. **Given** the retrieved context and user question, **When** the LLM generates a response, **Then** the response is displayed with the format "RESPOSTA: [answer]"
4. **Given** the CLI is running, **When** the user types a question and presses Enter, **Then** the response is returned and the system prompts for the next question

---

### User Story 3 - Out-of-Context Question Handling (Priority: P3)

As a user, I want the system to clearly indicate when my question cannot be answered from the document content, so that I know the information is not available rather than receiving fabricated answers.

**Why this priority**: Critical for trust and reliability, but only meaningful after basic Q&A (P2) works.

**Independent Test**: Can be fully tested by asking questions about topics not covered in the PDF and verifying the standard "information not available" response.

**Acceptance Scenarios**:

1. **Given** the user asks a question unrelated to the PDF content (e.g., "Qual a capital da Franca?"), **When** the system processes the query, **Then** it responds exactly: "Não tenho informações necessárias para responder sua pergunta."
2. **Given** the user asks for opinions or interpretations (e.g., "Voce acha isso bom ou ruim?"), **When** the system processes the query, **Then** it responds with the standard "information not available" message
3. **Given** the user asks about data not explicitly in the document (e.g., future projections not mentioned), **When** the system processes the query, **Then** it does not fabricate or extrapolate information

---

### Edge Cases

- What happens when the PDF file is empty or corrupted?
  - System displays an error message and does not create any database entries
- What happens when the database connection fails during ingestion?
  - System displays a connection error and suggests checking database status
- What happens when the user enters an empty question?
  - System prompts the user to enter a valid question
- What happens when the embedding API is unavailable?
  - System displays an error indicating the external service is unavailable
- What happens when the PDF contains only images without text?
  - System completes with a warning that no text content was found to index

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read PDF files and extract text content
- **FR-002**: System MUST split extracted text into chunks of 1000 characters with 150 character overlap
- **FR-003**: System MUST generate embedding vectors for each text chunk
- **FR-004**: System MUST store text chunks and their embeddings in a vector database
- **FR-005**: System MUST provide a command-line interface for users to input questions
- **FR-006**: System MUST convert user questions into embedding vectors
- **FR-007**: System MUST perform similarity search to retrieve the 10 most relevant chunks for each question
- **FR-008**: System MUST construct a prompt combining the retrieved context with the user question
- **FR-009**: System MUST send the prompt to an LLM and return the generated response
- **FR-010**: System MUST display responses in the format "RESPOSTA: [answer]"
- **FR-011**: System MUST respond with "Não tenho informações necessárias para responder sua pergunta." when the answer is not found in the context
- **FR-012**: System MUST never fabricate information or use knowledge external to the PDF content
- **FR-013**: System MUST never produce opinions or interpretations beyond what is written in the document
- **FR-014**: System MUST support continuous conversation until the user exits
- **FR-015**: System MUST load configuration from environment variables

### Key Entities

- **Document Chunk**: A segment of text extracted from the PDF (1000 chars with 150 overlap), with metadata about its source position
- **Embedding Vector**: A numerical representation of a text chunk that captures its semantic meaning, enabling similarity comparisons
- **User Query**: A question input by the user via CLI that will be vectorized and matched against stored embeddings
- **Context**: The concatenated text of the top 10 most similar chunks, provided to the LLM as the knowledge base for answering
- **Response**: The LLM-generated answer constrained to information present in the context

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully ingest a PDF document and receive confirmation of completion
- **SC-002**: Users receive accurate answers to questions about document content within 5 seconds of asking
- **SC-003**: 100% of questions outside the document context receive the standard "information not available" response
- **SC-004**: System correctly handles Portuguese language content including special characters
- **SC-005**: Users can conduct multiple consecutive questions in a single session without restarting
- **SC-006**: System provides clear error messages for all failure scenarios (missing file, database down, API unavailable)
- **SC-007**: Ingested document data persists across system restarts

## Assumptions

- The PDF document contains extractable text (not scanned images)
- Users have basic command-line familiarity
- Network connectivity is available for API calls to the embedding and LLM services
- The PostgreSQL database with pgVector extension is running and accessible
- Environment variables are properly configured before running the system
- The PDF size is reasonable for the configured chunk parameters (not excessively large)
