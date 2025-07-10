# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Data center deployment service module."""

from typing import Any, NamedTuple

import streamlit as st

from help_loader import get_cached_help_content
from kafka_events_helper import (
    DatacenterDeploymentEventData,
    TaskExecutionData,
    handle_datacenter_deployment_workflow,
)
from schema_protocols import DesignTopology, LocationMetro
from utils import select_options
from validation import (
    collect_validation_errors,
    validate_required_field,
    validate_required_selection,
)


class DeployDcFormState(NamedTuple):
    """State container for datacenter deployment form data."""

    change_number: str
    dc_name: str
    location_options: list[Any]
    location: str
    design_options: list[Any]
    design: str


def validate_data_center_form(state: DeployDcFormState) -> list[str]:
    """Validate Data Center deployment form fields and return a list of error messages.

    Returns:
        list[str]: List of validation error messages.

    """
    return collect_validation_errors(
        validate_required_field(state.change_number, "Change Number"),
        validate_required_field(state.dc_name, "Data Center Name"),
        validate_required_selection(state.location_options, state.location, "Location"),
        validate_required_selection(state.design_options, state.design, "Design Pattern"),
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

    if location_options:
        location = st.selectbox(
            "Location *",
            location_options,
            key="dc_location",
            help="Select the metro area where the data center will be deployed. This determines network connectivity and regional settings.",
        )
    else:
        location = st.text_input(
            "Location * (Manual Entry)",
            key="dc_location_manual",
            help="Enter the metro area manually. Contact support if location options are not loading.",
            placeholder="e.g., New York, London, Tokyo",
        )
        st.info("💡 Location options are not available. Using manual entry mode.")

    if design_options:
        design = st.selectbox(
            "Design Pattern *",
            design_options,
            key="dc_design",
            help="Choose the infrastructure design template. Different patterns provide varying levels of redundancy, capacity, and features.",
        )
    else:
        design = st.text_input(
            "Design Pattern * (Manual Entry)",
            key="dc_design_manual",
            help="Enter the design pattern manually. Common patterns: 'Standard', 'High-Availability', 'Edge'.",
            placeholder="e.g., Standard, High-Availability",
        )
        st.info("💡 Design pattern options are not available. Using manual entry mode.")

    return {
        "change_number": change_number,
        "dc_name": dc_name,
        "location_options": location_options,
        "location": location,
        "design_options": design_options,
        "design": design,
    }


def _create_success_callback(form_data: dict[str, Any]) -> callable:
    """Create a success callback function for the DC deployment workflow.

    Returns:
        callable: A function that displays the DC deployment success message.

    """

    def success_callback() -> None:
        st.success(
            f"✅ **Success!** Data Center '{form_data['dc_name']}' will be deployed at "
            f"{form_data['location']} with design '{form_data['design']}'. "
            f"**Change Number:** {form_data['change_number']}",
        )

        st.balloons()
        st.snow()
        next_steps = get_cached_help_content("dc-next-steps")
        st.markdown(next_steps)

    return success_callback


def _handle_validation_errors(errors: list[str]) -> None:
    """Handle and display validation errors."""
    st.error("❌ **Please fix the following issues:**")
    for err in errors:
        st.error(f"• {err}")
    validation_tips = get_cached_help_content("validation-tips")
    st.markdown(f"💡 {validation_tips}")


def _handle_successful_submission(form_data: dict[str, Any]) -> None:
    """Handle successful form submission using the global Kafka events helper."""
    # Create success callback
    success_callback = _create_success_callback(form_data)

    # Use the global helper to handle the complete workflow
    event_data = DatacenterDeploymentEventData(
        change_number=form_data["change_number"],
        dc_name=form_data["dc_name"],
        location=form_data["location"],
        design_pattern=form_data["design"],
        user_id=None,  # Could be enhanced to include actual user ID
    )

    task_data = TaskExecutionData(
        service_name=form_data["dc_name"],
        change_number=form_data["change_number"],
    )

    handle_datacenter_deployment_workflow(
        event_data=event_data,
        task_data=task_data,
        success_callback=success_callback,
    )


def deploy_dc_form() -> None:
    """Streamlit form for deploying a Data Center."""
    st.subheader("Deploy Data Center")

    # Form instructions
    instructions = get_cached_help_content("deploy-dc-instructions")
    st.markdown(f"📋 {instructions}")

    with st.form("deploy_data_center_form"):
        form_data = get_dc_form_data()

        submit_dc = st.form_submit_button("🚀 Submit Data Center Request", use_container_width=True)

        if submit_dc:
            form_state = DeployDcFormState(**form_data)
            errors = validate_data_center_form(form_state)

            if errors:
                _handle_validation_errors(errors)
            else:
                _handle_successful_submission(form_data)
