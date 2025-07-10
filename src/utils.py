# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Utility functions for the FRANC Service Portal."""

from typing import NamedTuple, TypedDict

import streamlit as st

from infrahub import (
    InfrahubClientSync,
    create_and_save,
    create_branch,
    get_client,
    get_dropdown_options,
)


class CreateObjectConfig(NamedTuple):
    """Configuration for creating and saving Infrahub objects."""

    object_name: str | None = None


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


def select_options(kind: type, **kwargs: SelectOptionsKwargs) -> list:
    """Safely get select options and show error if needed.

    Returns:
        List of select options with both display_label and id, or empty list if error occurs.

    """
    try:
        # Get the actual node objects instead of just display labels
        client = kwargs.get("client") or get_client(kwargs.get("branch", "main"))
        filters = kwargs.get("filters", {})
        branch = kwargs.get("branch", "main")

        nodes = client.filters(
            kind=kind,
            branch=branch,
            **filters,
        )

        # Return objects with both display label and id for use in forms
        return [{"label": node.display_label, "id": node.id} for node in nodes]
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


def init_dynamic_field_state(state_key: str, default_count: int = 1, default_value: str = "") -> None:
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


def create_deployment_branch(branch_name: str) -> bool:
    """Create a deployment branch with UI feedback.

    This is a global utility function that can be used across multiple services
    to create branches with consistent user interface feedback.

    Args:
        branch_name: The name of the branch to create

    Returns:
        bool: True if branch creation was successful, False otherwise

    """
    try:
        st.info("🔄 Creating deployment branch...")
        result = create_branch(branch_name)
    except ValueError as e:
        st.error(f"❌ **Deployment failed:** {e}")
        st.info("💡 Please check the error details above and try again.")
        return False
    else:
        if result.get("status") == "created":
            st.success(f"✅ **Branch created successfully:** {branch_name}")
            return True

        st.error("❌ **Branch creation failed**")
        st.info("💡 Please check the error details and try again.")
        return False


def create_and_save_object(
    kind: type,
    data: dict,
    branch: str = "main",
    config: CreateObjectConfig | None = None,
) -> object | None:
    """Create and save an object in Infrahub with UI feedback.

    This is a global utility function that can be used across multiple services
    to create and save objects with consistent user interface feedback.

    Args:
        kind: The schema kind/type of the object to create
        data: Dictionary containing the object data
        branch: The branch to create the object in (default: "main")
        config: Optional configuration for display name

    Returns:
        The created Infrahub object on success, None on failure

    """
    if config is None:
        config = CreateObjectConfig()

    object_name = config.object_name or getattr(kind, "__name__", str(kind))

    try:
        st.info(f"🔄 Creating {object_name}...")
        infrahub_object = create_and_save(kind=kind, data=data, branch=branch)
    except (ValueError, RuntimeError, ConnectionError) as e:
        st.error(f"❌ **{object_name} creation failed:** {e}")
        st.info("💡 Please check the error details above and try again.")
        return None
    else:
        st.success(f"✅ **{object_name} created successfully!**")
        return infrahub_object
