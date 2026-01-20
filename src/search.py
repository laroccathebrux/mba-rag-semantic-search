"""
Módulo de busca semântica para o sistema RAG.

Este módulo implementa a funcionalidade de busca e resposta a perguntas,
incluindo:
    1. Conexão com o vector store (pgVector)
    2. Busca por similaridade semântica
    3. Construção de contexto a partir dos resultados
    4. Formatação do prompt para o LLM
    5. Geração de respostas usando ChatGPT

O módulo segue a arquitetura RAG onde o contexto relevante é recuperado
do banco de dados vetorial e usado para fundamentar as respostas do LLM,
garantindo que as respostas sejam baseadas apenas no conteúdo do documento.

Configuração via variáveis de ambiente:
    - DATABASE_URL: URL de conexão com PostgreSQL
    - PG_VECTOR_COLLECTION_NAME: Nome da coleção no pgVector
    - OPENAI_API_KEY: Chave de API da OpenAI
    - OPENAI_EMBEDDING_MODEL: Modelo de embeddings (default: text-embedding-3-small)

Constantes importantes:
    - SIMILARITY_K: Número de chunks recuperados por consulta (10)
    - PROMPT_TEMPLATE: Template do prompt com regras de resposta

Author: Alessandro Silveira
Date: 2026-01-20
"""

import os
from typing import List, Optional, Tuple, Union

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações carregadas do ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
"""str: URL de conexão com o banco de dados PostgreSQL."""

PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
"""str: Nome da coleção onde os vetores estão armazenados."""

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
"""str: Chave de API da OpenAI para embeddings e LLM."""

OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
"""str: Modelo de embeddings da OpenAI a ser utilizado."""

# Configuração de busca conforme especificação do desafio
SIMILARITY_K = 10
"""int: Número de chunks mais similares a recuperar em cada busca."""

# Template do prompt conforme especificação do desafio
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
"""str: Template do prompt com regras para resposta contextualizada.

O template inclui:
    - Placeholder para o contexto recuperado
    - Regras estritas para resposta baseada apenas no contexto
    - Exemplos de perguntas fora do contexto e suas respostas padrão
    - Placeholder para a pergunta do usuário
"""


def get_embeddings() -> OpenAIEmbeddings:
    """
    Cria e retorna uma instância de OpenAIEmbeddings.

    Configura o cliente de embeddings da OpenAI com o modelo especificado
    nas variáveis de ambiente. Este cliente é usado para vetorizar as
    perguntas do usuário durante a busca por similaridade.

    Returns:
        OpenAIEmbeddings: Instância configurada do cliente de embeddings
            pronta para gerar vetores a partir de texto.

    Note:
        O mesmo modelo deve ser usado tanto na ingestão quanto na busca
        para garantir compatibilidade dos vetores.
    """
    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )


def get_vector_store() -> PGVector:
    """
    Inicializa e retorna a conexão com o vector store.

    Estabelece conexão com o PostgreSQL/pgVector usando as configurações
    de ambiente. O vector store permite buscar documentos por similaridade
    semântica usando os embeddings armazenados.

    Returns:
        PGVector: Instância do vector store conectada ao banco de dados,
            pronta para realizar buscas por similaridade.

    Raises:
        ConnectionError: Se a conexão com o banco de dados falhar.
            Isso pode ocorrer se o PostgreSQL não estiver rodando,
            se as credenciais estiverem incorretas, ou se a coleção
            não existir.

    Example:
        >>> store = get_vector_store()
        >>> results = store.similarity_search("pergunta", k=10)
    """
    try:
        embeddings = get_embeddings()
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=PG_VECTOR_COLLECTION_NAME,
            connection=DATABASE_URL,
        )
        return vector_store
    except Exception as e:
        if "connect" in str(e).lower() or "connection" in str(e).lower():
            raise ConnectionError(
                "Erro ao conectar ao banco de dados. Verifique se está rodando."
            ) from e
        raise


def get_llm() -> ChatOpenAI:
    """
    Cria e retorna uma instância de ChatOpenAI.

    Configura o cliente do ChatGPT com o modelo gpt-5-nano e temperature=0
    para respostas determinísticas e consistentes.

    Returns:
        ChatOpenAI: Instância configurada do cliente ChatGPT pronta
            para gerar respostas a partir de prompts.

    Note:
        A temperature=0 garante que o modelo produza respostas mais
        determinísticas, reduzindo a variabilidade nas respostas.
    """
    return ChatOpenAI(
        model="gpt-5-nano",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )


def search_similar(
    vector_store: PGVector, query: str
) -> List[Tuple[Document, float]]:
    """
    Busca documentos similares no vector store.

    Realiza uma busca por similaridade semântica, retornando os K chunks
    mais relevantes para a query fornecida. A similaridade é calculada
    usando distância de cosseno entre os vetores de embedding.

    Args:
        vector_store (PGVector): Instância do vector store onde buscar.
        query (str): Pergunta ou texto de busca do usuário.

    Returns:
        List[Tuple[Document, float]]: Lista de tuplas (documento, score)
            ordenadas por relevância (score decrescente). Cada documento
            contém o texto do chunk e seus metadados.

    Note:
        O valor de K (número de resultados) é definido pela constante
        SIMILARITY_K (10 por padrão, conforme especificação do desafio).

    Example:
        >>> results = search_similar(store, "Qual o faturamento?")
        >>> for doc, score in results:
        ...     print(f"Score: {score:.2f} - {doc.page_content[:50]}...")
    """
    results = vector_store.similarity_search_with_score(query, k=SIMILARITY_K)
    return results


def build_context(results: List[Tuple[Document, float]]) -> str:
    """
    Constrói a string de contexto a partir dos resultados da busca.

    Concatena o conteúdo textual de todos os documentos recuperados,
    separando cada chunk com duas quebras de linha para melhor legibilidade
    no prompt.

    Args:
        results (List[Tuple[Document, float]]): Lista de tuplas (documento, score)
            retornadas pela busca por similaridade.

    Returns:
        str: Texto concatenado de todos os documentos, com cada chunk
            separado por "\\n\\n". Retorna string vazia se a lista estiver vazia.

    Note:
        A ordem dos chunks no contexto segue a ordem de relevância
        retornada pela busca (mais relevante primeiro).

    Example:
        >>> context = build_context(results)
        >>> print(context[:100])
        "O faturamento da empresa em 2023 foi de 10 milhões..."
    """
    context_parts = [doc.page_content for doc, _ in results]
    return "\n\n".join(context_parts)


def format_prompt(contexto: str, pergunta: str) -> str:
    """
    Formata o template do prompt com contexto e pergunta.

    Substitui os placeholders {contexto} e {pergunta} no PROMPT_TEMPLATE
    pelos valores fornecidos, gerando o prompt final a ser enviado ao LLM.

    Args:
        contexto (str): Texto do contexto recuperado pela busca por similaridade.
        pergunta (str): Pergunta do usuário a ser respondida.

    Returns:
        str: Prompt formatado pronto para ser enviado ao LLM.

    Note:
        O template inclui regras estritas que instruem o LLM a:
        - Responder apenas com base no contexto
        - Usar resposta padrão para perguntas fora do contexto
        - Não inventar informações
        - Não emitir opiniões

    Example:
        >>> prompt = format_prompt("O céu é azul.", "Qual a cor do céu?")
        >>> print(prompt)
        CONTEXTO:
        O céu é azul.
        ...
    """
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["contexto", "pergunta"],
    )
    return prompt.format(contexto=contexto, pergunta=pergunta)


def search_prompt(question: Optional[str] = None) -> Optional[Union[str, bool]]:
    """
    Função principal de busca: inicializa componentes e executa consulta.

    Esta função serve dois propósitos:
    1. Quando chamada sem argumentos: inicializa e valida a conexão
    2. Quando chamada com pergunta: executa o pipeline completo de Q&A

    O pipeline de Q&A inclui:
    1. Conectar ao vector store
    2. Vetorizar a pergunta do usuário
    3. Buscar os 10 chunks mais similares
    4. Construir o contexto a partir dos chunks
    5. Formatar o prompt com contexto e pergunta
    6. Enviar ao LLM e retornar a resposta

    Args:
        question (Optional[str]): Pergunta do usuário a ser respondida.
            Se None, apenas inicializa os componentes e retorna True.

    Returns:
        Optional[Union[str, bool]]:
            - str: Resposta do LLM quando uma pergunta é fornecida
            - True: Quando chamada sem pergunta (indica inicialização OK)
            - None: Se ocorrer erro ou pergunta vazia

    Note:
        Esta função trata erros internamente, exibindo mensagens
        amigáveis ao usuário e retornando None em caso de falha.

    Example:
        >>> # Inicialização
        >>> if search_prompt():
        ...     print("Sistema pronto!")
        Sistema pronto!
        >>> # Consulta
        >>> resposta = search_prompt("Qual o faturamento?")
        >>> print(resposta)
        O faturamento foi de 10 milhões de reais.
    """
    try:
        # Inicializar componentes
        vector_store = get_vector_store()
        llm = get_llm()

        # Se não houver pergunta, apenas validar inicialização
        if question is None:
            return True

        # Validar pergunta
        if not question.strip():
            return None

        # Executar pipeline de Q&A
        results = search_similar(vector_store, question)
        context = build_context(results)
        formatted_prompt = format_prompt(context, question)

        # Gerar resposta
        response = llm.invoke(formatted_prompt)
        return response.content

    except ConnectionError as e:
        print(f"Erro: {e}")
        return None
    except Exception as e:
        print(f"Erro ao comunicar com serviço externo. Tente novamente. ({e})")
        return None
