"""
Módulo de interface CLI para o sistema RAG.

Este módulo fornece uma interface de linha de comando interativa para
que os usuários façam perguntas sobre o conteúdo do PDF ingerido.

Funcionalidades:
    - Loop interativo de perguntas e respostas
    - Suporte a múltiplas perguntas em sequência
    - Tratamento gracioso de erros e interrupções
    - Comandos de saída em português e inglês

Fluxo de uso:
    1. O usuário inicia o chat com `python src/chat.py`
    2. O sistema exibe o prompt "Faça sua pergunta:"
    3. O usuário digita uma pergunta
    4. O sistema processa e exibe a resposta
    5. O ciclo se repete até o usuário digitar um comando de saída

Comandos de saída:
    - sair: Encerra a sessão (português)
    - exit: Encerra a sessão (inglês)
    - quit: Encerra a sessão (inglês)

Formato de saída:
    PERGUNTA: [pergunta do usuário]
    RESPOSTA: [resposta baseada no PDF]

Author: Alessandro Silveira
Date: 2026-01-20
"""

from search import search_prompt

# Comandos que encerram a sessão do chat
EXIT_COMMANDS = {"sair", "exit", "quit"}
"""set: Conjunto de comandos que encerram a sessão do chat.

Inclui variantes em português (sair) e inglês (exit, quit) para
maior conveniência do usuário.
"""


def main() -> None:
    """
    Ponto de entrada principal para a aplicação de chat CLI.

    Esta função implementa o loop principal de interação com o usuário:
    1. Inicializa a conexão com o sistema de busca
    2. Exibe o prompt inicial
    3. Aceita perguntas do usuário em loop contínuo
    4. Processa cada pergunta e exibe a resposta
    5. Continua até receber comando de saída ou interrupção

    O tratamento de erros inclui:
    - Falha na inicialização: exibe mensagem e encerra
    - Entrada vazia: ignora e solicita nova pergunta
    - KeyboardInterrupt (Ctrl+C): encerra graciosamente
    - EOFError: encerra graciosamente

    Returns:
        None

    Note:
        As respostas seguem o formato especificado no desafio:
        "RESPOSTA: [conteúdo da resposta]"

        Perguntas fora do contexto do documento recebem a resposta padrão:
        "Não tenho informações necessárias para responder sua pergunta."

    Example:
        $ python src/chat.py
        Faça sua pergunta:

        PERGUNTA: Qual o faturamento da empresa?
        RESPOSTA: O faturamento foi de 10 milhões de reais.

        PERGUNTA: sair
        $
    """
    # Inicializar o sistema de busca
    # search_prompt() sem argumentos retorna True se inicialização OK
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    # Exibir prompt inicial
    print("Faça sua pergunta:\n")

    try:
        # Loop principal de interação
        while True:
            try:
                # Solicitar entrada do usuário
                question = input("PERGUNTA: ").strip()
            except EOFError:
                # Fim de arquivo (ex: pipe fechado)
                break

            # Ignorar entrada vazia
            if not question:
                continue

            # Verificar comando de saída (case-insensitive)
            if question.lower() in EXIT_COMMANDS:
                break

            # Processar pergunta e obter resposta
            response = search_prompt(question)

            # Exibir resposta
            if response:
                print(f"RESPOSTA: {response}\n")
            else:
                print("RESPOSTA: Erro ao processar sua pergunta. Tente novamente.\n")

    except KeyboardInterrupt:
        # Tratamento gracioso de Ctrl+C
        print("\n")


if __name__ == "__main__":
    """
    Executa a aplicação de chat quando o módulo é executado diretamente.

    Exemplo de uso:
        $ python src/chat.py
    """
    main()
