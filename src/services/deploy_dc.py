# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Data center deployment service module."""

from typing import Any, NamedTuple

import streamlit as st

from help_loader import get_cached_help_content
from infrahub import create_and_save, create_branch
from schema_protocols import DesignTopology, LocationMetro
from utils import select_options
from validation import (
    collect_validation_errors,
    validate_required_field,
    validate_required_selection,
)
from workflow_engine import WorkflowEngine


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


def _show_success_message(form_data: dict[str, Any]) -> None:
    """Display DC deployment success message.

    Args:
        form_data: The validated form data containing DC configuration

    """
    st.success(
        f"**Change Number:** {form_data['change_number']} submited for deployment!",
    )

    st.balloons()
    st.snow()
    next_steps = get_cached_help_content("dc-next-steps")
    st.markdown(next_steps)


def _handle_validation_errors(errors: list[str]) -> None:
    """Handle and display validation errors."""
    st.error("❌ **Please fix the following issues:**")
    for err in errors:
        st.error(f"• {err}")
    validation_tips = get_cached_help_content("validation-tips")
    st.markdown(f"💡 {validation_tips}")


def _handle_successful_submission(form_data: dict[str, Any]) -> None:
    """Handle successful form submission with multi-step Infrahub workflow."""
    # Create workflow engine for DC deployment
    workflow = WorkflowEngine("Data Center Deployment")
    branch_name = f"implement_{form_data.get('change_number', '').lower()}"

    # Add workflow steps - simple and reusable pattern
    workflow.add_step(
        "Creating deployment branch",
        create_branch,
        branch_name,
    )

    # Example: Add context-aware steps that create objects and reference them later
    # These use the old pattern (context-based) for object references
    
    # Uncomment these lines to add object creation steps with references:
    # workflow.add_step(
    #     "Creating metro location",
    #     create_metro_location_step,
    #     form_data,
    #     # This step uses context parameter pattern
    # )
    
    # workflow.add_step(
    #     "Creating topology design",
    #     create_design_topology_step,
    #     form_data,
    #     # This step references the metro location created in the previous step
    # )

    # Execute workflow - only show success if all steps completed successfully
    try:
        # Initialize context with branch name for reference
        initial_context = {"branch_name": branch_name}
        result = workflow.execute_with_status(initial_context)
        if result.error_count == 0:
            _show_success_message(form_data)
        else:
            st.error(f"❌ **Deployment failed:** {result.error_count} step(s) failed")
            st.info("💡 Please check the error details above and try again.")
    except ValueError as e:
        st.error(f"❌ **Deployment failed:** {e}")
        st.info("💡 Please check the error details above and try again.")


# Helper functions for object creation with references
def create_metro_location_step(form_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Create a metro location and store it in context for later reference.

    Args:
        form_data: Form data containing location information
        context: Workflow context for storing references

    Returns:
        dict[str, Any]: Step result with created object information

    """
    branch_name = context.get("branch_name", "main")

    metro = create_and_save(
        LocationMetro,
        {
            "name": form_data["location"],
            "shortname": form_data["location"][:10],
            "description": f"Metro location for {form_data['dc_name']}",
        },
        branch=branch_name,
    )

    # Store the created object in context for later use
    context["metro_location"] = metro
    context["metro_location_id"] = metro.id

    return {
        "status": "created",
        "node_id": str(metro.id),
        "name": metro.name,
        "message": f"Created metro location: {metro.name}",
        "object_reference": metro.id,  # Store reference for later use
    }


def create_design_topology_step(form_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Create a topology design that can reference other objects.

    Args:
        form_data: Form data containing design information
        context: Workflow context containing object references

    Returns:
        dict[str, Any]: Step result with created object information

    """
    branch_name = context.get("branch_name", "main")

    # Optional: Get metro location from context if it exists
    metro_location_id = context.get("metro_location_id")

    design_data = {
        "name": f"{form_data['dc_name']}-{form_data['design']}",
        "description": f"Topology design for {form_data['dc_name']} using {form_data['design']} pattern",
        "type": "DC",
    }

    # Add location reference if available
    if metro_location_id:
        design_data["location"] = metro_location_id

    design = create_and_save(
        DesignTopology,
        design_data,
        branch=branch_name,
    )

    # Store the design in context
    context["topology_design"] = design
    context["topology_design_id"] = design.id

    location_info = f" at {context.get('metro_location', {}).get('name', 'unknown location')}" if metro_location_id else ""

    return {
        "status": "created",
        "node_id": str(design.id),
        "name": design.name,
        "message": f"Created topology design: {design.name}{location_info}",
        "object_reference": design.id,
    }


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
