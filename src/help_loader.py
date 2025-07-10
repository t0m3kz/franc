# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Help content loader utility for the Service Portal.

Loads help content from markdown files in the src/help directory.
"""

from pathlib import Path

import streamlit as st


def get_help_content(help_file: str) -> str:
    """Load help content from a markdown file.

    Args:
        help_file: Name of the help file (without .md extension)

    Returns:
        Content of the help file or error message if file not found

    """
    try:
        help_path = Path(__file__).parent / "help" / f"{help_file}.md"
        if help_path.exists():
            return help_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return f"Error loading help content: {e}"
    else:
        return f"Help content not found: {help_file}.md"


def show_help_section(title: str, help_file: str, icon: str = "📖") -> None:
    """Display a help section using content from a markdown file.

    Args:
        title: Title for the expandable help section
        help_file: Name of the help file (without .md extension)
        icon: Icon to display with the title

    """
    with st.expander(f"{icon} {title}"):
        content = get_help_content(help_file)
        st.markdown(content)


def load_help_content(help_file: str) -> str | None:
    """Load help content and return it, with error handling.

    Args:
        help_file: Name of the help file (without .md extension)

    Returns:
        Content string or None if error occurred

    """
    try:
        help_path = Path(__file__).parent / "help" / f"{help_file}.md"
        if help_path.exists():
            return help_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        st.error(f"Error loading help: {e}")
        return None
    else:
        st.error(f"Help file not found: {help_file}.md")
        return None


# Cache help content to avoid repeated file reads
@st.cache_data
def get_cached_help_content(help_file: str) -> str:
    """Cache help content loader for better performance.

    Args:
        help_file: Name of the help file (without .md extension)

    Returns:
        Content of the help file

    """
    return get_help_content(help_file)
