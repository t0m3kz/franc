# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Unified form utilities for streamlit forms across FRANC services."""

from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypedDict, TypeVar

import streamlit as st

from .help_loader import get_cached_help_content
from .validation import collect_validation_errors, validate_required_field

# --- Field Configurations ---
T = TypeVar("T")


class SchemaProtocol(Protocol):
    """Protocol for schema types."""


@dataclass
class DropdownField(Generic[T]):
    """Represents a dropdown field for Streamlit forms.

    Attributes
    ----------
    schema_type : type[T]
        The type of the schema for the dropdown options.
    field_name : str
        The name of the field in the form data.
    display : str
        The display label for the dropdown field.
    help : str
        Help text for the dropdown field.
    placeholder : str, optional
        Placeholder text for the dropdown (default is "").
    required : bool, optional
        Whether the field is required (default is True).
    filters : dict[str, Any], optional
        Filters to apply to the dropdown options (default is empty dict).
    prefix : str, optional
        Prefix for the field name (default is "field").

    """

    schema_type: type[T]
    field_name: str
    display: str
    help: str
    placeholder: str = ""
    required: bool = True
    filters: dict[str, Any] = field(default_factory=dict)
    prefix: str = "field"


@dataclass
class AttributeDropdownField(Generic[T]):
    """Represents a dropdown field for a specific attribute in Streamlit forms.

    Attributes
    ----------
    schema_type : type[T]
        The type of the schema for the dropdown options.
    attr : str
        The attribute name in the schema to use for the dropdown.
    display : str
        The display label for the dropdown field.
    help : str
        Help text for the dropdown field.
    placeholder : str, optional
        Placeholder text for the dropdown (default is "").
    required : bool, optional
        Whether the field is required (default is True).
    prefix : str, optional
        Prefix for the field name (default is "field").

    """

    schema_type: type[T]
    attr: str
    display: str
    help: str
    placeholder: str = ""
    required: bool = True
    prefix: str = "field"


@dataclass
class InputField:
    """Represents a text input field for Streamlit forms.

    Attributes
    ----------
    field_name : str
        The name of the field in the form data.
    display : str
        The display label for the field.
    help : str
        Help text for the field.
    placeholder : str, optional
        Placeholder text for the input (default is "").
    required : bool, optional
        Whether the field is required (default is True).
    prefix : str, optional
        Prefix for the field name (default is "field").
    multiline : bool, optional
        Whether the input is multiline (default is False).

    """

    field_name: str
    display: str
    help: str
    placeholder: str = ""
    required: bool = True
    prefix: str = "field"
    multiline: bool = False


# --- Validation ---
class ObjectFormData(TypedDict, total=False):
    """TypedDict for object form data.

    Attributes
    ----------
    name : str
        The name of the object.
    description : str
        The description of the object.
    # ... add more fields as needed

    """

    name: str
    description: str
    # ... add more fields as needed


def validate_object_form(form_data: ObjectFormData, required_fields: list[str]) -> list[str]:
    """Validate required fields in object form data.

    Parameters
    ----------
    form_data : ObjectFormData
        The form data to validate.
    required_fields : list[str]
        List of required field names.

    Returns
    -------
    list[str]
        List of validation error messages.

    """
    validation_results = []
    for field_name in required_fields:
        field_display_name = field_name.replace("_", " ").title()
        validation_results.append(validate_required_field(str(form_data.get(field_name, "")), field_display_name))
    return collect_validation_errors(*validation_results)


# --- Submission & Success ---
def display_validation_errors(errors: list[str]) -> None:
    """Display validation errors in the Streamlit UI.

    Parameters
    ----------
    errors : list[str]
        A list of error messages to display.

    """
    if errors:
        pass
    st.error("❌ **Please fix the following issues:**")
    for err in errors:
        st.error(f"• {err}")
    validation_tips = get_cached_help_content("validation-tips")
    st.markdown(f"💡 {validation_tips}")
