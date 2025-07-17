# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Data center deployment service module."""

from typing import Any, NamedTuple

import streamlit as st

from infrahub import create_and_save, create_branch
from schema_protocols import DesignTopology, IpamPrefix, LocationMetro, TopologyDataCenter
from utils import handle_validation_errors, select_options, show_help_section
from validation import (
    collect_validation_errors,
    validate_required_field,
)


class DeployDcFormState(NamedTuple):
    """State container for datacenter deployment form data."""

    change_number: str
    dc_name: str
    location: str
    design: str
    management: str
    technical: str
    customer: str
    public: str


def validate_data_center_form(state: DeployDcFormState) -> list[str]:
    """Validate Data Center deployment form fields and return a list of error messages.

    Returns:
        list[str]: List of validation error messages.

    """
    return collect_validation_errors(
        validate_required_field(state.change_number, "Change Number"),
        validate_required_field(state.dc_name, "Data Center Name"),
        validate_required_field(state.management, "Management Pool"),
        validate_required_field(state.technical, "Technical Pool"),
        validate_required_field(state.customer, "Customer Pool"),
    )


def get_dc_form_data() -> dict[str, Any]:
    """Collect form input data for DC deployment.

    Returns:
        dict[str, Any]: Dictionary containing all DC deployment form data.

    """
    change_number = st.text_input(
        "Change Number *",
        key="dc_change_number",
        help="Enter the change management number for this data center deployment request. This is required for tracking and approval.",
        placeholder="e.g., CHG-2024-001234",
    )

    location_options = select_options(LocationMetro)
    design_options = select_options(DesignTopology, filters={"type__value": "DC"})

    dc_name = st.text_input(
        "Data Center Name *",
        key="dc_name",
        help="Enter a unique name for the data center. Use a descriptive name that includes "
        "location or purpose (e.g., 'NYC-Main-DC', 'London-Edge-01')",
        placeholder="e.g., NYC-Main-DC",
    )

    location = None
    if location_options:
        location_label_to_id = {str(opt): getattr(opt, "id", str(opt)) for opt in location_options}
        location_label = st.selectbox(
            "Location *",
            list(location_label_to_id.keys()),
            key="dc_location",
            help="Select the metro area where the data center will be deployed. This determines network connectivity and regional settings.",
        )
        location = location_label_to_id[location_label]

    design = None
    if design_options:
        design_label_to_id = {str(opt): getattr(opt, "id", str(opt)) for opt in design_options}
        design_label = st.selectbox(
            "Design Pattern *",
            list(design_label_to_id.keys()),
            key="dc_design",
            help="Choose the infrastructure design template. Different patterns provide varying levels of redundancy, capacity, and features.",
        )
        design = design_label_to_id[design_label]

    management = st.text_input(
        "Management Pool *",
        key="dc_management_pool",
        help="Enter the management IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.0.0/24",
    )

    technical = st.text_input(
        "Technical Pool *",
        key="dc_technical_pool",
        help="Enter the technical IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.1.0/24",
    )

    customer = st.text_input(
        "Customer Pool *",
        key="dc_customer_pool",
        help="Enter the customer IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.2.0/24",
    )

    public = st.text_input(
        "Public Pool *",
        key="dc_public_pool",
        help="Enter the public IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.3.0/24",
    )

    return {
        "change_number": change_number,
        "dc_name": dc_name,
        "location": location,
        "design": design,
        "management": management,
        "technical": technical,
        "customer": customer,
        "public": public,
    }


def _handle_successful_submission(form_data: dict[str, Any]) -> None:
    """Handle successful form submission with multi-step Infrahub workflow."""
    branch_name = f"implement_{form_data.get('change_number', '').lower()}"
    prefixes = [
        {
            "prefix": form_data["management"],
            "status": "active",
            "role": "management",
        },
        {
            "prefix": form_data["technical"],
            "status": "active",
            "role": "technical",
        },
        {
            "prefix": form_data["customer"],
            "status": "active",
            "role": "customer",
        },
    ]

    if form_data["public"]:
        prefixes.append(
            {
                "prefix": form_data["public"],
                "status": "active",
                "role": "public",
            },
        )

    st.info(f"Creating deployment branch: {branch_name}")
    create_branch(branch_name)

    st.info("Creating necessary subnets")
    subnet_ids = {}
    for prefix in prefixes:
        result = create_and_save(
            kind=IpamPrefix,
            data=prefix,
            branch=branch_name,
        )
        subnet_ids[prefix["role"]] = result.id
        st.success(f"✅ Creating subnet for role: {prefix['role']} with prefix: {prefix['prefix']}")

    st.info("Creating topology data center object...")
    topology_data = {
        "name": form_data["dc_name"],
        "description": f"Auto-generated topology for {form_data['dc_name']}",
        "strategy": "ospf-ibgp",
        "provider": {"hfid": "Technology Partner"},  # Placeholder for provider
        "design": {"hfid": form_data["design"]},
        "location": {"hfid": [form_data["location"]]},
        "management_subnet": subnet_ids.get("management"),
        "customer_subnet": subnet_ids.get("customer"),
        "technical_subnet": subnet_ids.get("technical"),
        "public_subnet": subnet_ids.get("public"),
        "member_of_groups": [{"hfid": "topologies_dc"}]
    }
    result = create_and_save(kind=TopologyDataCenter, data=topology_data, branch=branch_name)
    st.success("✅ All steps completed. Data Center deployment workflow finished.")
    st.balloons()
    st.snow()
    show_help_section("Next steps", "dc-next-steps")


def deploy_dc_form() -> None:
    """Streamlit form for deploying a Data Center."""
    st.subheader("Deploy Data Center")

    # Form instructions
    show_help_section("Deployment Instructions", "deploy-dc-instructions", icon="📋")

    with st.form("deploy_data_center_form"):
        form_data = get_dc_form_data()

        submit_dc = st.form_submit_button("🚀 Submit Data Center Request", use_container_width=True)

        if submit_dc:
            form_state = DeployDcFormState(**form_data)
            errors = validate_data_center_form(form_state)

            if errors:
                handle_validation_errors(errors)
            else:
                _handle_successful_submission(form_data)
