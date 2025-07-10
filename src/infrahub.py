"""Infrahub integration module.

Copyright (c) 2024 FRANC Service Portal
All rights reserved.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from fast_depends import Depends, inject
from infrahub_sdk import Config, InfrahubClientSync

if TYPE_CHECKING:
    from infrahub_sdk.branch import BranchData
    from infrahub_sdk.client import SchemaTypeSync


class AttributeNotFoundError(Exception):
    """Exception raised when a specified attribute is not found for a given kind."""


def get_client(branch: str = "main") -> InfrahubClientSync:
    """Get Infrahub client for the specified branch.

    Args:
        branch: The branch name to use (default: "main")

    Returns:
        InfrahubClientSync: Configured Infrahub client instance

    Raises:
        ConnectionError: If INFRAHUB_ADDRESS environment variable is not set

    """
    address = os.environ.get("INFRAHUB_ADDRESS")
    if not address:
        msg = "INFRAHUB_ADDRESS environment variable is not set. Please configure Infrahub connection."
        raise ConnectionError(msg)

    # Ensure branch is not None
    if branch is None:
        branch = "main"

    return InfrahubClientSync(address=address, config=Config(default_branch=branch))


@inject(cast=False)  # type: ignore[call-overload]
def create_and_save(
    kind: type[SchemaTypeSync],
    data: dict,
    branch: str = "main",
    client: InfrahubClientSync = Depends(get_client),
) -> SchemaTypeSync:
    """Create a new Infrahub node and save it.

    Args:
        kind: The kind of the node to create.
        data: The data to create the node with.
        branch: The branch to create the node in.
        client: The Infrahub client to use.

    Returns:
        The created Infrahub node.

    """
    infrahub_node = client.create(
        kind=kind,
        branch=branch,
        **data,
    )
    infrahub_node.save(allow_upsert=True)
    return infrahub_node


@inject(cast=False)  # type: ignore[call-overload]
def filter_nodes(
    kind: type[SchemaTypeSync],
    filters: dict | None = None,
    include: list[str] | None = None,
    branch: str = "main",
    client: InfrahubClientSync = Depends(get_client),
) -> list[SchemaTypeSync]:
    """Filter nodes by kind, branch, include and filters.

    Returns:
        A list of nodes.

    """
    filters = filters or {}
    return client.filters(
        kind=kind,
        branch=branch,
        include=include,
        prefetch_relationships=True,
        **filters,
    )


@inject(cast=False)
def get_select_options(
    kind: type[SchemaTypeSync],
    filters: dict | None = None,
    branch: str = "main",
    client: InfrahubClientSync = Depends(get_client),
) -> list[dict[str, str]]:
    """Filter nodes by kind, branch, include and filters.

    Returns:
        A list of display labels for the nodes.

    """
    filters = filters or {}
    return [
        node.display_label
        for node in client.filters(
            kind=kind,
            branch=branch,
            **filters,
        )
    ]


@inject(cast=False)  # type: ignore[call-overload]
def get_dropdown_options(
    kind: str | type[SchemaTypeSync],
    attribute_name: str,
    branch: str = "main",
    client: InfrahubClientSync = Depends(get_client),
) -> list[str]:
    """Get dropdown options for a given attribute.

    Raises:
        Exception: If the attribute is not found.

    Returns:
        A list of dropdown options for the given attribute.

    """
    # Get schema for this kind

    schema = client.schema.get(kind=kind, branch=branch)

    # Find desired attribute
    matched_attribute = next((att for att in schema.attributes if att.name == attribute_name), None)

    if matched_attribute is None:
        msg = f"Can't find attribute `{attribute_name}` for kind `{kind}`"
        raise Exception(msg)
    return [choice["name"] for choice in matched_attribute.choices]


@inject
def create_branch(branch_name: str, client: InfrahubClientSync = Depends(get_client)) -> BranchData:
    """Create a new branch.

    Args:
        branch_name: The name of the branch to create.
        client: The Infrahub client to use.

    Returns:
        The created branch.

    """
    return client.branch.create(branch_name=branch_name, sync_with_git=False)
