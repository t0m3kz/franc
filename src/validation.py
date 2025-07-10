# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Validation utilities for the Service Portal forms.

This module provides a comprehensive set of validation functions for form fields,
supporting type-safe validation with consistent error messaging and performance optimization.
"""

import ipaddress
from collections import Counter

# Constants for validation
MIN_VPC_GROUP_MEMBERS = 2


def validate_required_field(value: str | None, field_name: str) -> str | None:
    """Validate that a required field is not empty or whitespace-only.

    Args:
        value: The field value to validate (can be None or string)
        field_name: Human-readable name of the field for error messages

    Returns:
        Error message if field is invalid, None if valid

    Examples:
        >>> validate_required_field("hello", "Name")
        None
        >>> validate_required_field("", "Name")
        'Name is required.'
        >>> validate_required_field(None, "Name")
        'Name is required.'

    """
    if value is None or not value.strip():
        return f"{field_name} is required."
    return None


def validate_required_selection(options: list[str], selected_value: str | None, field_name: str) -> str | None:
    """Validate that a selection field has a valid value when options are available.

    Args:
        options: List of valid option values
        selected_value: The selected value to validate
        field_name: Human-readable name of the field for error messages

    Returns:
        Error message if selection is invalid, None if valid

    Examples:
        >>> validate_required_selection(["A", "B"], "A", "Choice")
        None
        >>> validate_required_selection(["A", "B"], "C", "Choice")
        'Choice is required.'
        >>> validate_required_selection([], "", "Choice")
        None

    """
    # No validation needed if no options available
    if not options:
        return None

    # Check if selection is missing or invalid
    if not selected_value or selected_value not in options:
        return f"{field_name} is required."
    return None


def validate_unique_names(names: list[str], field_name: str = "Names") -> str | None:
    """Validate that a list of names contains only unique, non-empty values.

    Args:
        names: List of name strings to validate for uniqueness
        field_name: Human-readable name of the field for error messages

    Returns:
        Error message if names are not unique, None if valid

    Examples:
        >>> validate_unique_names(["A", "B", "C"], "Interface")
        None
        >>> validate_unique_names(["A", "B", "A"], "Interface")
        'Interfaces must be unique. Duplicates found: A'

    """
    # Filter out empty/whitespace-only names and strip whitespace
    names_clean = [name.strip() for name in names if name.strip()]

    # Use Counter for efficient duplicate detection
    name_counts = Counter(names_clean)
    duplicates = [name for name, count in name_counts.items() if count > 1]

    if duplicates:
        # Ensure proper pluralization
        plural_field = field_name if field_name.endswith("s") else f"{field_name}s"
        duplicates_str = ", ".join(sorted(duplicates))
        return f"{plural_field} must be unique. Duplicates found: {duplicates_str}"

    return None


def validate_minimum_count(items: list[str], min_count: int, field_name: str) -> str | None:
    """Validate that a list has at least the minimum number of valid (non-empty) items.

    Args:
        items: List of items to validate
        min_count: Minimum required count of valid items
        field_name: Human-readable name of the field for error messages

    Returns:
        Error message if minimum count not met, None if valid

    Examples:
        >>> validate_minimum_count(["A", "B", "C"], 2, "item")
        None
        >>> validate_minimum_count(["A"], 2, "item")
        'At least 2 items are required.'
        >>> validate_minimum_count(["A"], 1, "item")
        None

    """
    # Count only non-empty items (after stripping whitespace)
    valid_items = [item for item in items if item.strip()]

    if len(valid_items) < min_count:
        # Handle proper pluralization and grammar
        plural_field = field_name if min_count == 1 else f"{field_name}s"
        verb = "is" if min_count == 1 else "are"
        return f"At least {min_count} {plural_field} {verb} required."

    return None


def collect_validation_errors(*validators: str | None) -> list[str]:
    """Collect all non-None, non-empty validation error messages.

    Args:
        *validators: Variable number of validation error messages (or None)

    Returns:
        List of valid error messages, with empty strings and None values filtered out

    Examples:
        >>> collect_validation_errors("Error 1", None, "Error 2", "")
        ['Error 1', 'Error 2']
        >>> collect_validation_errors(None, None)
        []

    """
    return [error.strip() for error in validators if error is not None and error.strip()]


def validate_vpc_groups(vpcs: list[bool], vpc_groups: list[str]) -> list[str]:
    """Validate that each vPC group has at least the minimum required number of interfaces.

    Args:
        vpcs: List of boolean flags indicating if each interface is part of a vPC
        vpc_groups: List of vPC group names corresponding to each interface

    Returns:
        List of problematic group names that have too few members

    Raises:
        ValueError: If vpcs and vpc_groups lists have different lengths

    Examples:
        >>> validate_vpc_groups([True, True, False], ["group1", "group1", ""])
        []
        >>> validate_vpc_groups([True, False], ["group1", ""])
        ['group1']

    """
    if len(vpcs) != len(vpc_groups):
        msg = f"vpcs and vpc_groups must have same length: {len(vpcs)} != {len(vpc_groups)}"
        raise ValueError(msg)

    # Count members in each vPC group using Counter for efficiency
    vpc_group_counts: dict[str, int] = {}

    for is_vpc, group_name in zip(vpcs, vpc_groups, strict=True):
        group = group_name.strip()
        # Only count non-empty groups for vPC-enabled interfaces
        if is_vpc and group:
            vpc_group_counts[group] = vpc_group_counts.get(group, 0) + 1

    # Return groups with insufficient members
    return [group_name for group_name, count in vpc_group_counts.items() if count < MIN_VPC_GROUP_MEMBERS]


def validate_ip_subnet(value: str | None, field_name: str) -> str | None:
    """Validate that a field contains a valid IP subnet/network.

    Args:
        value: The field value to validate (can be None or string)
        field_name: The name of the field being validated (for error messages)

    Returns:
        str | None: Error message if validation fails, None if valid

    Examples:
        >>> validate_ip_subnet("192.168.1.0/24", "Customer Subnet")
        None
        >>> validate_ip_subnet("invalid", "Customer Subnet")
        'Customer Subnet must be a valid IP subnet (e.g., 192.168.1.0/24)'
        >>> validate_ip_subnet("", "Customer Subnet")
        'Customer Subnet is required'

    """
    if value is None or not value.strip():
        return f"{field_name} is required"

    try:
        # Try to parse as IP network
        ipaddress.ip_network(value.strip(), strict=False)
    except ValueError:
        return f"{field_name} must be a valid IP subnet (e.g., 192.168.1.0/24)"
    else:
        return None


def validate_ip_subnet_optional(value: str | None, field_name: str) -> str | None:
    """Validate that a field contains a valid IP subnet/network, allowing empty values.

    Args:
        value: The field value to validate (can be None or string)
        field_name: The name of the field being validated (for error messages)

    Returns:
        str | None: Error message if validation fails, None if valid or empty

    Examples:
        >>> validate_ip_subnet_optional("192.168.1.0/24", "Public Subnet")
        None
        >>> validate_ip_subnet_optional("", "Public Subnet")
        None
        >>> validate_ip_subnet_optional("invalid", "Public Subnet")
        'Public Subnet must be a valid IP subnet (e.g., 192.168.1.0/24)'

    """
    if value is None or not value.strip():
        return None

    try:
        # Try to parse as IP network
        ipaddress.ip_network(value.strip(), strict=False)
    except ValueError:
        return f"{field_name} must be a valid IP subnet (e.g., 192.168.1.0/24)"
    else:
        return None
