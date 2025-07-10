# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Validation utilities for the Service Portal forms."""


def validate_required_field(value: str, field_name: str) -> str | None:
    """Validate that a required field is not empty.

    Returns:
        Error message if field is empty, None otherwise.

    """
    if not value.strip():
        return f"{field_name} is required."
    return None


def validate_required_selection(options: list, selected_value: str, field_name: str) -> str | None:
    """Validate that a required selection field has a value when options are available.

    Returns:
        Error message if selection is required but not provided, None otherwise.

    """
    if options and not selected_value:
        return f"{field_name} is required."
    return None


def validate_unique_names(names: list[str], field_name: str = "Names") -> str | None:
    """Validate that a list of names contains only unique, non-empty values.

    Returns:
        Error message if names are not unique, None otherwise.

    """
    names_clean = [n.strip() for n in names if n.strip()]
    if len(names_clean) != len(set(names_clean)):
        return f"{field_name} must be unique and non-empty."
    return None


def validate_minimum_count(items: list, min_count: int, field_name: str) -> str | None:
    """Validate that a list has at least the minimum number of valid items.

    Returns:
        Error message if minimum count not met, None otherwise.

    """
    valid_items = [item for item in items if str(item).strip()]
    if len(valid_items) < min_count:
        return f"At least {min_count} {field_name.lower()} {'is' if min_count == 1 else 'are'} required."
    return None


def collect_validation_errors(*validators: str | None) -> list[str]:
    """Collect all non-None validation error messages.

    Returns:
        List of validation error messages.

    """
    return [error for error in validators if error is not None]


def validate_vpc_groups(vpcs: list[bool], vpc_groups: list[str]) -> list[str]:
    """Validate that each vPC group (non-empty) has at least two interfaces assigned.

    Returns:
        List of problematic group names (with too few members).

    """
    vpc_group_counts: dict[str, int] = {}
    for vpc, group_name in zip(vpcs, vpc_groups, strict=True):
        group = group_name.strip()
        if vpc and group:
            vpc_group_counts.setdefault(group, 0)
            vpc_group_counts[group] += 1
    min_vpc_members = 2
    return [g for g, count in vpc_group_counts.items() if count < min_vpc_members]
