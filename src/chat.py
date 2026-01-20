"""CLI chat interface for RAG system.

This module provides a command-line interface for users to ask questions
about the ingested PDF content.
"""

from typing import NoReturn

from search import search_prompt


EXIT_COMMANDS = {"sair", "exit", "quit"}


def main() -> None:
    """Entry point for CLI chat application.

    Displays a prompt, accepts user questions, and returns answers
    based on the ingested PDF content. Loops until user exits.
    """
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta:\n")

    try:
        while True:
            try:
                question = input("PERGUNTA: ").strip()
            except EOFError:
                break

            if not question:
                continue

            if question.lower() in EXIT_COMMANDS:
                break

            response = search_prompt(question)

            if response:
                print(f"RESPOSTA: {response}\n")
            else:
                print("RESPOSTA: Erro ao processar sua pergunta. Tente novamente.\n")

    except KeyboardInterrupt:
        print("\n")


if __name__ == "__main__":
    main()
