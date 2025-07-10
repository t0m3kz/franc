# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Utility functions for the FRANC Service Portal."""

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


def get_dynamic_list(key: str, default: str, num: int) -> list[str]:
    """Get or initialize a dynamic list from session state for a given key and length.

    Returns:
        List of string values from session state.

    """
    vals = st.session_state.get(f"{key}_values", [])
    if len(vals) < num:
        vals += [default] * (num - len(vals))
    if len(vals) > num:
        vals = vals[:num]
    st.session_state[f"{key}_values"] = vals
    return vals


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


def init_dynamic_field_state(state_key: str, default_count: int = 1, default_value: str = "") -> None:
    """Initialize session state for a dynamic field list."""
    if f"num_{state_key}" not in st.session_state:
        st.session_state[f"num_{state_key}"] = default_count
    if f"{state_key}_values" not in st.session_state:
        st.session_state[f"{state_key}_values"] = [default_value] * default_count


def update_dynamic_field_state(state_key: str) -> None:
    """Update session state for a dynamic field list when count changes."""
    n = int(st.session_state[f"num_{state_key}"])
    current = st.session_state.get(f"{state_key}_values", [])
    if len(current) < n:
        st.session_state[f"{state_key}_values"] = current + [""] * (n - len(current))
    elif len(current) > n:
        st.session_state[f"{state_key}_values"] = current[:n]
