# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Unit tests for help loader functionality."""

from unittest.mock import patch

from src.help_loader import get_cached_help_content, show_help_section


class TestHelpLoader:
    """Test help content loading functionality."""

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_get_cached_help_content_success(self, mock_exists, mock_read_text):
        """Test successful help content loading."""
        mock_exists.return_value = True
        mock_read_text.return_value = "# Test Help\n\nThis is test help content."

        result = get_cached_help_content("test-help")

        assert result == "# Test Help\n\nThis is test help content."
        mock_exists.assert_called_once()
        mock_read_text.assert_called_once_with(encoding="utf-8")

    @patch("pathlib.Path.exists")
    def test_get_cached_help_content_file_not_found(self, mock_exists):
        """Test help content loading when file doesn't exist."""
        mock_exists.return_value = False

        result = get_cached_help_content("nonexistent-help")

        assert "Help content not found" in result

    @patch("streamlit.markdown")
    @patch("streamlit.expander")
    @patch("src.help_loader.get_help_content")
    def test_show_help_section(self, mock_get_content, mock_expander, mock_markdown):
        """Test showing help section in expandable format."""
        mock_get_content.return_value = "Test help content"
        mock_expander_obj = mock_expander.return_value
        mock_expander_obj.__enter__ = lambda _: mock_expander_obj
        mock_expander_obj.__exit__ = lambda *_: None

        show_help_section("Test Section", "test-help")

        mock_expander.assert_called_once_with("📖 Test Section")
        mock_get_content.assert_called_once_with("test-help")
        mock_markdown.assert_called_once_with("Test help content")
