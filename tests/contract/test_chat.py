"""Contract tests for chat.py module."""

import os
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestChatInputOutput:
    """Contract tests for chat.py input/output format."""

    @patch("chat.search_prompt")
    def test_chat_displays_prompt(self, mock_search_prompt, capsys):
        """Test that chat displays 'Faça sua pergunta:' prompt."""
        mock_search_prompt.side_effect = [True, "Resposta de teste"]

        with patch("builtins.input", side_effect=["pergunta", "sair"]):
            from chat import main
            main()

        captured = capsys.readouterr()
        assert "Faça sua pergunta:" in captured.out

    @patch("chat.search_prompt")
    def test_chat_displays_resposta_format(self, mock_search_prompt, capsys):
        """Test that responses are displayed with 'RESPOSTA:' prefix."""
        mock_search_prompt.side_effect = [True, "Resposta de teste"]

        with patch("builtins.input", side_effect=["pergunta", "sair"]):
            from chat import main
            main()

        captured = capsys.readouterr()
        assert "RESPOSTA:" in captured.out

    @patch("chat.search_prompt")
    def test_chat_exits_on_sair(self, mock_search_prompt, capsys):
        """Test that chat exits when user types 'sair'."""
        mock_search_prompt.return_value = True

        with patch("builtins.input", return_value="sair"):
            from chat import main
            main()

        captured = capsys.readouterr()
        assert "Faça sua pergunta:" in captured.out

    @patch("chat.search_prompt")
    def test_chat_exits_on_exit(self, mock_search_prompt, capsys):
        """Test that chat exits when user types 'exit'."""
        mock_search_prompt.return_value = True

        with patch("builtins.input", return_value="exit"):
            from chat import main
            main()

    @patch("chat.search_prompt")
    def test_chat_exits_on_quit(self, mock_search_prompt, capsys):
        """Test that chat exits when user types 'quit'."""
        mock_search_prompt.return_value = True

        with patch("builtins.input", return_value="quit"):
            from chat import main
            main()

    @patch("chat.search_prompt")
    def test_chat_handles_empty_input(self, mock_search_prompt, capsys):
        """Test that chat re-prompts on empty input."""
        mock_search_prompt.side_effect = [True, "Resposta"]

        with patch("builtins.input", side_effect=["", "pergunta", "sair"]):
            from chat import main
            main()

        assert mock_search_prompt.call_count >= 2

    @patch("chat.search_prompt")
    def test_chat_handles_keyboard_interrupt(self, mock_search_prompt, capsys):
        """Test that chat handles Ctrl+C gracefully."""
        mock_search_prompt.return_value = True

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            from chat import main
            main()

    @patch("chat.search_prompt")
    def test_chat_displays_error_on_initialization_failure(self, mock_search_prompt, capsys):
        """Test that chat displays error when initialization fails."""
        mock_search_prompt.return_value = None

        from chat import main
        main()

        captured = capsys.readouterr()
        assert "Não foi possível iniciar o chat" in captured.out


class TestChatExitCommands:
    """Tests for chat exit commands."""

    def test_exit_commands_are_lowercase(self):
        """Test that exit commands are checked in lowercase."""
        from chat import EXIT_COMMANDS
        assert all(cmd.islower() for cmd in EXIT_COMMANDS)

    def test_exit_commands_include_all_variants(self):
        """Test that all exit command variants are included."""
        from chat import EXIT_COMMANDS
        assert "sair" in EXIT_COMMANDS
        assert "exit" in EXIT_COMMANDS
        assert "quit" in EXIT_COMMANDS
