# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MBA challenge project implementing a **RAG (Retrieval-Augmented Generation)** system with:
- **Ingestion**: Read PDF documents and store embeddings in PostgreSQL with pgVector
- **Search**: CLI-based semantic search using LangChain to answer questions based on PDF content

## Commands

### Database Setup
```bash
docker compose up -d
```

### Run PDF Ingestion
```bash
python src/ingest.py
```

### Start CLI Chat
```bash
python src/chat.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Data Flow
1. **Ingestion Pipeline** (`src/ingest.py`):
   - Load PDF using `PyPDFLoader`
   - Split into chunks (1000 chars, 150 overlap) using `RecursiveCharacterTextSplitter`
   - Generate embeddings using OpenAI `text-embedding-3-small`
   - Store vectors in PostgreSQL/pgVector using `langchain_postgres.PGVector`

2. **Query Pipeline** (`src/search.py` + `src/chat.py`):
   - Receive user question via CLI
   - Vectorize question and perform similarity search (k=10)
   - Build prompt with context from retrieved chunks
   - Call LLM (`gpt-5-nano`) to generate response
   - Return answer constrained to document context only

### Key Constraints
- Responses must be based **only** on PDF content
- Questions outside context must return: "Não tenho informações necessárias para responder sua pergunta."
- No external knowledge or opinions allowed

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=<your-key>
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
GOOGLE_API_KEY=<optional>
GOOGLE_EMBEDDING_MODEL=models/embedding-001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=<collection-name>
PDF_PATH=document.pdf
```

### Database
- PostgreSQL 17 with pgVector extension
- Default credentials: postgres/postgres
- Database name: rag
- Port: 5432

## Required Packages (Key Dependencies)
- `langchain` / `langchain-core` / `langchain-community`
- `langchain-openai` (embeddings and LLM)
- `langchain-postgres` (PGVector integration)
- `langchain-text-splitters` (RecursiveCharacterTextSplitter)
- `pypdf` (PDF loading)
- `psycopg` / `psycopg-binary` (PostgreSQL driver)
- `pgvector` (vector extension support)
- `python-dotenv` (environment variables)

## Project Structure
```
├── docker-compose.yml      # PostgreSQL + pgVector setup
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── document.pdf           # PDF to be ingested
├── src/
│   ├── ingest.py          # PDF ingestion script
│   ├── search.py          # Search logic with prompt template
│   └── chat.py            # CLI interface
└── README.md
```

## Active Technologies
- Python 3.x (required by MBA challenge) + LangChain (langchain, langchain-core, langchain-community, langchain-openai, langchain-postgres, langchain-text-splitters), pypdf (001-rag-semantic-search)
- PostgreSQL 17 with pgVector extension (Docker) (001-rag-semantic-search)

## Recent Changes
- 001-rag-semantic-search: Added Python 3.x (required by MBA challenge) + LangChain (langchain, langchain-core, langchain-community, langchain-openai, langchain-postgres, langchain-text-splitters), pypdf
