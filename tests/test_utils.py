# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.
"""Unit tests for utils.py."""
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str((Path(__file__).parent / ".." / "src").resolve()))
import utils


def test_get_dynamic_list_initializes(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr(utils, "st", mock_st)
    mock_st.session_state = {}
    result = utils.get_dynamic_list("foo", "bar", 3)
    assert result == ["bar", "bar", "bar"]
    assert mock_st.session_state["foo_values"] == ["bar", "bar", "bar"]


def test_get_dynamic_list_extends(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr(utils, "st", mock_st)
    mock_st.session_state = {"foo_values": ["a"]}
    result = utils.get_dynamic_list("foo", "b", 3)
    assert result == ["a", "b", "b"]


def test_get_dynamic_list_truncates(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr(utils, "st", mock_st)
    mock_st.session_state = {"foo_values": ["a", "b", "c", "d"]}
    result = utils.get_dynamic_list("foo", "x", 2)
    assert result == ["a", "b"]


def test_init_dynamic_field_state(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr(utils, "st", mock_st)
    mock_st.session_state = {}
    utils.init_dynamic_field_state("bar", 2, "baz")
    assert mock_st.session_state["num_bar"] == 2
    assert mock_st.session_state["bar_values"] == ["baz", "baz"]


def test_update_dynamic_field_state(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr(utils, "st", mock_st)
    mock_st.session_state = {"num_bar": 3, "bar_values": ["a"]}
    utils.update_dynamic_field_state("bar")
    assert mock_st.session_state["bar_values"] == ["a", "", ""]
    mock_st.session_state = {"num_bar": 2, "bar_values": ["a", "b", "c"]}
    utils.update_dynamic_field_state("bar")
    assert mock_st.session_state["bar_values"] == ["a", "b"]


def test_handle_validation_errors(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr(utils, "st", mock_st)
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    mock_st.markdown = MagicMock()
    monkeypatch.setattr(utils, "show_help_section", MagicMock(return_value="Some tips"))
    utils.handle_validation_errors(["err1", "err2"])
    mock_st.error.assert_any_call("❌ **Please fix the following issues:**")
    mock_st.error.assert_any_call("• err1")
    mock_st.error.assert_any_call("• err2")
    mock_st.markdown.assert_called_with("💡 Some tips")
