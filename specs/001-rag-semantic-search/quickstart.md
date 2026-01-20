# Quickstart: RAG Semantic Search System

**Feature**: 001-rag-semantic-search
**Date**: 2026-01-20

## Prerequisites

Before starting, ensure you have:

- [ ] Python 3.x installed
- [ ] Docker and Docker Compose installed
- [ ] OpenAI API key
- [ ] A PDF document to ingest

## Setup (5 minutes)

### 1. Clone and Navigate

```bash
cd /path/to/desafio_01
```

### 2. Create Environment File

Copy the example and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Database

```bash
docker compose up -d
```

Wait for healthy status:

```bash
docker compose ps
# Should show postgres_rag as "healthy"
```

### 5. Place Your PDF

Copy your PDF document to the project root:

```bash
cp /path/to/your/document.pdf ./document.pdf
```

## Usage

### Ingest PDF

Run once to process and store your document:

```bash
python src/ingest.py
```

Expected output:

```
Ingestão concluída: 42 chunks processados
```

### Start Chat

Launch the Q&A interface:

```bash
python src/chat.py
```

### Ask Questions

```
Faça sua pergunta:

PERGUNTA: Qual o faturamento da empresa?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos funcionários temos?
RESPOSTA: A empresa possui 150 funcionários.

PERGUNTA: Qual a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

### Exit

Type `sair`, `exit`, or `quit` to end the session.

## Troubleshooting

### Database not starting

```bash
docker compose down
docker compose up -d
docker compose logs postgres
```

### Connection refused

Ensure database is running and port 5432 is available:

```bash
docker compose ps
lsof -i :5432
```

### Empty responses

Check if ingestion completed:

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
```

### API errors

Verify your OpenAI API key:

```bash
echo $OPENAI_API_KEY
# Or check .env file
```

## Verification Checklist

After setup, verify:

- [ ] `docker compose ps` shows postgres_rag as healthy
- [ ] `python src/ingest.py` completes without errors
- [ ] `python src/chat.py` shows "Faça sua pergunta:" prompt
- [ ] Questions about PDF content return accurate answers
- [ ] Questions outside PDF return standard "Não tenho informações" message

## Clean Restart

To start fresh:

```bash
docker compose down -v  # Remove volumes (data)
docker compose up -d    # Restart clean
python src/ingest.py    # Re-ingest PDF
```
