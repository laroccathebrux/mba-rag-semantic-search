"""
Testes de contrato para o módulo chat.py.

Este módulo contém testes que verificam o contrato de interface do chat CLI,
garantindo que os formatos de entrada e saída seguem a especificação do sistema.

Os testes validam:
    - Exibição correta do prompt "Faça sua pergunta:"
    - Formato de resposta com prefixo "RESPOSTA:"
    - Comandos de saída (sair, exit, quit)
    - Tratamento de entrada vazia e interrupção do usuário
    - Mensagens de erro apropriadas

Classes de teste:
    TestChatInputOutput: Testes de contrato para entrada/saída.
    TestChatExitCommands: Testes para comandos de saída.
"""

import os
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestChatInputOutput:
    """Testes de contrato para formato de entrada/saída do chat.py."""

    @patch("chat.search_prompt")
    def test_chat_displays_prompt(self, mock_search_prompt, capsys):
        """
        Testa que o chat exibe o prompt 'Faça sua pergunta:'.

        Cenário: Usuário inicia o chat CLI.
        Esperado: Sistema exibe prompt em português solicitando pergunta.
        """
        mock_search_prompt.side_effect = [True, "Resposta de teste"]

        with patch("builtins.input", side_effect=["pergunta", "sair"]):
            from chat import main
            main()

        captured = capsys.readouterr()
        assert "Faça sua pergunta:" in captured.out

    @patch("chat.search_prompt")
    def test_chat_displays_resposta_format(self, mock_search_prompt, capsys):
        """
        Testa que as respostas são exibidas com prefixo 'RESPOSTA:'.

        Cenário: Sistema processa pergunta e gera resposta.
        Esperado: Resposta é exibida com prefixo "RESPOSTA:" para clareza.
        """
        mock_search_prompt.side_effect = [True, "Resposta de teste"]

        with patch("builtins.input", side_effect=["pergunta", "sair"]):
            from chat import main
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA:" in captured.out

    @patch("chat.search_prompt")
    def test_chat_exits_on_sair(self, mock_search_prompt, capsys):
        """
        Testa que o chat encerra quando usuário digita 'sair'.

        Cenário: Usuário deseja encerrar o chat digitando comando em português.
        Esperado: Sistema reconhece 'sair' e encerra graciosamente.
        """
        mock_search_prompt.return_value = True

        with patch("builtins.input", return_value="sair"):
            from chat import main
            main()

        captured = capsys.readouterr()
        assert "Faça sua pergunta:" in captured.out

    @patch("chat.search_prompt")
    def test_chat_exits_on_exit(self, mock_search_prompt, capsys):
        """
        Testa que o chat encerra quando usuário digita 'exit'.

        Cenário: Usuário deseja encerrar usando comando em inglês.
        Esperado: Sistema reconhece 'exit' e encerra graciosamente.
        """
        mock_search_prompt.return_value = True

        with patch("builtins.input", return_value="exit"):
            from chat import main
            main()

    @patch("chat.search_prompt")
    def test_chat_exits_on_quit(self, mock_search_prompt, capsys):
        """
        Testa que o chat encerra quando usuário digita 'quit'.

        Cenário: Usuário deseja encerrar usando comando alternativo em inglês.
        Esperado: Sistema reconhece 'quit' e encerra graciosamente.
        """
        mock_search_prompt.return_value = True

        with patch("builtins.input", return_value="quit"):
            from chat import main
            main()

    @patch("chat.search_prompt")
    def test_chat_handles_empty_input(self, mock_search_prompt, capsys):
        """
        Testa que o chat solicita nova pergunta quando input é vazio.

        Cenário: Usuário pressiona Enter sem digitar pergunta.
        Esperado: Sistema continua no loop solicitando nova pergunta.
        """
        mock_search_prompt.side_effect = [True, "Resposta"]

        with patch("builtins.input", side_effect=["", "pergunta", "sair"]):
            from chat import main
            main()

        assert mock_search_prompt.call_count >= 2

    @patch("chat.search_prompt")
    def test_chat_handles_keyboard_interrupt(self, mock_search_prompt, capsys):
        """
        Testa que o chat trata Ctrl+C graciosamente.

        Cenário: Usuário pressiona Ctrl+C para interromper o chat.
        Esperado: Sistema encerra sem exibir stack trace ou erro feio.
        """
        mock_search_prompt.return_value = True

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            from chat import main
            main()

    @patch("chat.search_prompt")
    def test_chat_displays_error_on_initialization_failure(self, mock_search_prompt, capsys):
        """
        Testa que o chat exibe erro quando a inicialização falha.

        Cenário: Conexão com banco de dados ou OpenAI API falha.
        Esperado: Sistema exibe mensagem amigável informando que não foi
                  possível iniciar o chat.
        """
        mock_search_prompt.return_value = None

        from chat import main
        main()

        captured = capsys.readouterr()
        assert "Não foi possível iniciar o chat" in captured.out


class TestChatExitCommands:
    """Testes para os comandos de saída do chat."""

    def test_exit_commands_are_lowercase(self):
        """
        Testa que os comandos de saída são verificados em minúsculas.

        Cenário: Validação da configuração dos comandos de saída.
        Esperado: Todos os comandos na lista EXIT_COMMANDS estão em minúsculas
                  para permitir comparação case-insensitive.
        """
        from chat import EXIT_COMMANDS
        assert all(cmd.islower() for cmd in EXIT_COMMANDS)

    def test_exit_commands_include_all_variants(self):
        """
        Testa que todas as variantes de comando de saída estão incluídas.

        Cenário: Validação da configuração dos comandos de saída.
        Esperado: Lista inclui 'sair' (PT-BR), 'exit' e 'quit' (EN).
        """
        from chat import EXIT_COMMANDS
        assert "sair" in EXIT_COMMANDS
        assert "exit" in EXIT_COMMANDS
        assert "quit" in EXIT_COMMANDS
