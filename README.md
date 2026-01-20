# RAG Semantic Search System

Sistema de busca semântica com RAG (Retrieval-Augmented Generation) para ingestão de documentos PDF e resposta a perguntas via CLI.

## Objetivo

Este projeto implementa um software capaz de:

- **Ingestão**: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector
- **Busca**: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF

## Tecnologias

- **Linguagem**: Python 3.x
- **Framework**: LangChain
- **Banco de dados**: PostgreSQL 17 + pgVector
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI gpt-5-nano
- **Infraestrutura**: Docker & Docker Compose

## Pré-requisitos

- Python 3.x instalado
- Docker e Docker Compose instalados
- Chave de API da OpenAI

## Instalação

### 1. Clone o repositório

```bash
git clone git@github-personal:laroccathebrux/mba-rag-semantic-search.git
cd mba-rag-semantic-search
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_chunks
PDF_PATH=document.pdf
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Inicie o banco de dados

```bash
docker compose up -d
```

Aguarde o banco ficar healthy:

```bash
docker compose ps
# Deve mostrar postgres_rag como "healthy"
```

### 5. Coloque seu PDF

Copie seu documento PDF para a raiz do projeto:

```bash
cp /caminho/para/seu/documento.pdf ./document.pdf
```

## Uso

### Ingestão do PDF

Execute uma vez para processar e armazenar o documento:

```bash
python src/ingest.py
```

Saída esperada:

```
Ingestão concluída: 42 chunks processados
```

### Iniciar o Chat

Inicie a interface de perguntas e respostas:

```bash
python src/chat.py
```

### Fazer Perguntas

```
Faça sua pergunta:

PERGUNTA: Qual o faturamento da empresa?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos funcionários temos?
RESPOSTA: A empresa possui 150 funcionários.

PERGUNTA: Qual a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

### Sair

Digite `sair`, `exit` ou `quit` para encerrar a sessão.

## Estrutura do Projeto

```
├── docker-compose.yml      # Configuração PostgreSQL + pgVector
├── requirements.txt        # Dependências Python
├── .env.example           # Template de variáveis de ambiente
├── document.pdf           # PDF para ingestão
├── README.md              # Este arquivo
└── src/
    ├── ingest.py          # Script de ingestão do PDF
    ├── search.py          # Lógica de busca e prompt
    └── chat.py            # Interface CLI
```

## Configuração

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| Chunk size | 1000 caracteres | Tamanho de cada fragmento de texto |
| Chunk overlap | 150 caracteres | Sobreposição entre fragmentos |
| k | 10 | Número de resultados na busca por similaridade |

## Troubleshooting

### Banco de dados não inicia

```bash
docker compose down
docker compose up -d
docker compose logs postgres
```

### Conexão recusada

Verifique se o banco está rodando e a porta 5432 está disponível:

```bash
docker compose ps
lsof -i :5432
```

### Respostas vazias

Verifique se a ingestão foi concluída:

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
```

### Erros de API

Verifique sua chave da OpenAI:

```bash
echo $OPENAI_API_KEY
```

## Reinicialização Completa

Para começar do zero:

```bash
docker compose down -v  # Remove volumes (dados)
docker compose up -d    # Reinicia limpo
python src/ingest.py    # Re-ingere o PDF
```

## Licença

Projeto desenvolvido como parte do MBA em Inteligência Artificial.
