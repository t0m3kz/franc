# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Data center deployment service module."""

from typing import Any, NamedTuple

import streamlit as st

from infrahub import create_and_save, create_branch
from schema_protocols import (
    DesignTopology,
    IpamPrefix,
    LocationMetro,
    TopologyDataCenter,
)
from utils import handle_validation_errors, select_options, show_help_section
from validation import (
    collect_validation_errors,
    validate_required_field,
)


class DataCenterFormState(NamedTuple):
    """Represents the state of the Data Center deployment form.

    Attributes:
        change_number (str): The change request number.
        dc_name (str): The name of the data center.
        location (str): The location identifier for the data center.
        design (str): The design identifier for the data center.
        management (str): The management IP prefix/subnet.
        technical (str): The technical IP prefix/subnet.
        customer (str): The customer IP prefix/subnet.
        public (str): The public IP prefix/subnet.

    """

    change_number: str
    dc_name: str
    location: str
    design: str
    management: str
    technical: str
    customer: str
    public: str


def validate_data_center_form(state: DataCenterFormState) -> list[str]:
    """Validate Data Center deployment form fields and return a list of error messages.

    Returns:
        list[str]: A list of error messages for invalid or missing fields.

    """
    return collect_validation_errors(
        validate_required_field(state.change_number, "Change Number"),
        validate_required_field(state.dc_name, "Data Center Name"),
        validate_required_field(state.management, "Management Pool"),
        validate_required_field(state.technical, "Technical Pool"),
        validate_required_field(state.customer, "Customer Pool"),
    )


def render_dc_form() -> tuple[DataCenterFormState | None, bool]:
    """Render the simplified data center deployment form.

    Returns:
        A tuple containing the DataCenterFormState (or None) and a boolean indicating if the form was submitted.

    """
    with st.form("deploy_data_center_form", border=False):
        change_number = st.session_state.get("change_number")
        dc_name = st.session_state.get("dc_name")
        location = st.session_state.get("location")
        design = st.session_state.get("design")
        management = st.session_state.get("management")
        technical = st.session_state.get("technical")
        customer = st.session_state.get("customer")
        public = st.session_state.get("public")
        submit = st.form_submit_button(
            "🚀 Submit Data Center Request", use_container_width=True
        )
        if submit:
            state = DataCenterFormState(
                change_number=change_number,
                dc_name=dc_name,
                location=location,
                design=design,
                management=management,
                technical=technical,
                customer=customer,
                public=public,
            )
            return state, True
        return None, False


def infrahub_deploy(form_data: dict[str, Any]) -> None:
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
        st.success(
            f"✅ Creating subnet for role: {prefix['role']} with prefix: {prefix['prefix']}"
        )

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
        "member_of_groups": [{"hfid": "topologies_dc"}],
    }
    result = create_and_save(
        kind=TopologyDataCenter, data=topology_data, branch=branch_name
    )
    st.success("✅ All steps completed. Data Center deployment workflow finished.")
    st.balloons()
    st.snow()
    show_help_section("Next steps", "dc-next-steps")


def deploy_dc_form() -> None:
    """Streamlit form for deploying a Data Center."""
    st.subheader("Deploy Data Center")
    show_help_section("Deployment Instructions", "deploy-dc-instructions", icon="📋")
    st.text_input(
        "Change Number *",
        key="change_number",
        help="This is required for tracking and approval.",
        placeholder="e.g., CHG-2024-001234",
    )
    st.text_input(
        "Data Center Name *",
        key="dc_name",
        help="Enter a unique name for the data center.",
        placeholder="e.g., NYC-Main-DC",
    )
    st.selectbox(
        "Location *",
        select_options(LocationMetro),
        key="location",
        help="Choose the city where DC is located.",
    )
    st.selectbox(
        "Design *",
        select_options(DesignTopology, filters={"type__value": "DC"}),
        key="design",
        help="Choose the design for the data center.",
    )
    st.text_input(
        "Management Pool *",
        key="management",
        help="Enter the management IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.0.0/24",
    )
    st.text_input(
        "Technical Pool *",
        key="technical",
        help="Enter the technical IP prefix/subnet.",
        placeholder="e.g., 10.0.1.0/24",
    )
    st.text_input(
        "Customer Pool *",
        key="customer",
        help="Enter the customer IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.2.0/24",
    )
    st.text_input(
        "Public Pool *",
        key="public",
        help="Enter the public IP prefix/subnet for the data center (required).",
        placeholder="e.g., 10.0.3.0/24",
    )
    state, submitted = render_dc_form()
    if submitted and state:
        errors = validate_data_center_form(state)
        if errors:
            handle_validation_errors(errors)
        else:
            infrahub_deploy(state._asdict())
