# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.
"""Utility functions for Streamlit app."""
from pathlib import Path
from typing import TypedDict

import streamlit as st

from infrahub import InfrahubClientSync, get_dropdown_options, get_select_options


class SelectOptionsKwargs(TypedDict, total=False):
    """Type definition for select_options kwargs."""

    filters: dict | None
    branch: str
    client: InfrahubClientSync


class DropdownOptionsKwargs(TypedDict, total=False):
    """Type definition for dropdown_options kwargs."""

    attribute_name: str
    branch: str
    client: InfrahubClientSync


def handle_validation_errors(
    errors: list[str], help_key: str = "validation-tips"
) -> None:
    """Handle and display validation errors in Streamlit.

    Args:
        errors: List of error messages to display.
        help_key: Key for help content to show tips (default: "validation-tips").

    """
    st.error("❌ **Please fix the following issues:**")
    for err in errors:
        st.error(f"• {err}")
    validation_tips = None
    try:
        validation_tips = show_help_section("Validation Tips", help_key)
    except (OSError, UnicodeDecodeError):
        validation_tips = None
    if validation_tips:
        st.markdown(f"💡 {validation_tips}")


def select_options(kind: type, **kwargs: SelectOptionsKwargs) -> list:
    """Safely get select options and show error if needed.

    Returns:
        List of select options, or empty list if error occurs.

    """
    try:
        return get_select_options(kind=kind, **kwargs)
    except (RuntimeError, ConnectionError) as e:
        st.error(f"Could not load {kind.__name__} options: {e}")
        return []


def dropdown_options(kind: type, **kwargs: DropdownOptionsKwargs) -> list:
    """Safely get dropdown options and show error if needed.

    Returns:
        List of dropdown options, or empty list if error occurs.

    """
    try:
        return get_dropdown_options(kind=kind, **kwargs)
    except (RuntimeError, ConnectionError) as e:
        st.error(f"Could not load {kind.__name__} options: {e}")
        return []


def get_dynamic_list(key: str, default: str, num: int) -> list[str]:
    """Get or initialize a dynamic list from session state for a given key and length.

    This function combines initialization and updating of dynamic field state.

    Args:
        key: The base key for session state storage
        default: Default value for new list items
        num: Required number of items in the list

    Returns:
        List of string values from session state, properly sized.

    """
    # Initialize if not exists
    if f"{key}_values" not in st.session_state:
        st.session_state[f"{key}_values"] = [default] * num
        return st.session_state[f"{key}_values"]

    # Get current values and adjust size
    vals = st.session_state[f"{key}_values"]

    if len(vals) < num:
        # Extend list with default values
        vals.extend([default] * (num - len(vals)))
    elif len(vals) > num:
        # Truncate list to required size
        vals = vals[:num]

    # Update session state and return
    st.session_state[f"{key}_values"] = vals
    return vals


def init_dynamic_field_state(
    state_key: str, default_count: int = 1, default_value: str = ""
) -> None:
    """Initialize session state for a dynamic field list.

    Note: This function is kept for backward compatibility.
    Consider using get_dynamic_list() for new code as it combines init and update.
    """
    if f"num_{state_key}" not in st.session_state:
        st.session_state[f"num_{state_key}"] = default_count
    if f"{state_key}_values" not in st.session_state:
        st.session_state[f"{state_key}_values"] = [default_value] * default_count


def update_dynamic_field_state(state_key: str) -> None:
    """Update session state for a dynamic field list when count changes.

    Note: This function is kept for backward compatibility.
    Consider using get_dynamic_list() for new code as it combines init and update.
    """
    n = int(st.session_state[f"num_{state_key}"])
    current = st.session_state.get(f"{state_key}_values", [])
    if len(current) < n:
        st.session_state[f"{state_key}_values"] = current + [""] * (n - len(current))
    elif len(current) > n:
        st.session_state[f"{state_key}_values"] = current[:n]


# --- Help content loader functions ---


def show_help_section(title: str, help_file: str, icon: str = "📖") -> None:
    """Display a help section using content from a markdown file, with error handling.

    Args:
        title: Title for the expandable help section
        help_file: Name of the help file (without .md extension)
        icon: Icon to display with the title

    """
    with st.expander(f"{icon} {title}"):
        try:
            help_path = Path(__file__).parent / "help" / f"{help_file}.md"
            if help_path.exists():
                content = help_path.read_text(encoding="utf-8")
                st.markdown(content)
            else:
                st.error(f"Help file not found: {help_file}.md")
        except (OSError, UnicodeDecodeError) as e:
            st.error(f"Error loading help: {e}")
