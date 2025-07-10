# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""PoP deployment service module."""

from typing import Any, NamedTuple

import streamlit as st

from help_loader import get_cached_help_content
from schema_protocols import DesignTopology, LocationMetro, OrganizationProvider
from utils import select_options
from validation import (
    collect_validation_errors,
    validate_required_field,
    validate_required_selection,
)


class DeployPopFormState(NamedTuple):
    """State container for PoP deployment form data."""

    change_number: str
    pop_name: str
    location_options: list[Any]
    location: str
    design_options: list[Any]
    design: str
    provider_options: list[Any]
    provider: str


def validate_pop_form(state: DeployPopFormState) -> list[str]:
    """Validate PoP deployment form fields and return a list of error messages.

    Returns:
        list[str]: List of validation error messages.

    """
    return collect_validation_errors(
        validate_required_field(state.change_number, "Change Number"),
        validate_required_field(state.pop_name, "PoP Name"),
        validate_required_selection(state.location_options, state.location, "Location"),
        validate_required_selection(state.design_options, state.design, "Design Pattern"),
        validate_required_selection(state.provider_options, state.provider, "Provider"),
    )


def get_pop_form_data() -> dict[str, Any]:
    """Collect form input data for PoP deployment.

    Returns:
        dict[str, Any]: Dictionary containing all PoP deployment form data.

    """
    change_number = st.text_input(
        "Change Number *",
        key="pop_change_number",
        help="Enter the change management number for this PoP deployment request. This is required for tracking and approval.",
        placeholder="e.g., CHG-2024-001234",
    )

    location_options = select_options(LocationMetro)
    design_options = select_options(DesignTopology, filters={"type__value": "POP"})
    provider_options = select_options(OrganizationProvider)

    pop_name = st.text_input(
        "PoP Name *",
        key="pop_name",
        help="Enter a unique name for the Point of Presence. Include location and purpose "
        "(e.g., 'Miami-Edge-01', 'Seattle-Peering-Hub')",
        placeholder="e.g., Miami-Edge-01",
    )

    if location_options:
        location = st.selectbox(
            "Location *",
            location_options,
            key="pop_location",
            help="Select the metro area for the PoP deployment. This affects network latency and provider availability.",
        )
    else:
        location = st.text_input(
            "Location * (Manual Entry)",
            key="pop_location_manual",
            help="Enter the metro area manually. Contact support if location options are not loading.",
            placeholder="e.g., Miami, Seattle, Frankfurt",
        )
        st.info("💡 Location options are not available. Using manual entry mode.")

    if design_options:
        design = st.selectbox(
            "Design Pattern *",
            design_options,
            key="pop_design",
            help="Choose the PoP design template. Options may include edge, peering hub, or standard configurations.",
        )
    else:
        design = st.text_input(
            "Design Pattern * (Manual Entry)",
            key="pop_design_manual",
            help="Enter the design pattern manually. Common patterns: 'Edge', 'Peering-Hub', 'Standard'.",
            placeholder="e.g., Edge, Peering-Hub",
        )
        st.info("💡 Design pattern options are not available. Using manual entry mode.")

    if provider_options:
        provider = st.selectbox(
            "Provider *",
            provider_options,
            key="pop_provider",
            help="Select the network service provider for this PoP. This determines connectivity options and SLAs.",
        )
    else:
        provider = st.text_input(
            "Provider * (Manual Entry)",
            key="pop_provider_manual",
            help="Enter the provider name manually. Contact support if provider options are not loading.",
            placeholder="e.g., Equinix, Digital Realty, AWS",
        )
        st.info("💡 Provider options are not available. Using manual entry mode.")

    return {
        "change_number": change_number,
        "pop_name": pop_name,
        "location_options": location_options,
        "location": location,
        "design_options": design_options,
        "design": design,
        "provider_options": provider_options,
        "provider": provider,
    }


def _create_success_callback(form_data: dict[str, Any]) -> callable:
    """Create a success callback function for the PoP deployment workflow.

    Returns:
        callable: A function that displays the PoP deployment success message.

    """

    def success_callback() -> None:
        st.success(
            f"✅ **Success!** PoP '{form_data['pop_name']}' will be deployed at {form_data['location']} "
            f"with design '{form_data['design']}' and provider '{form_data['provider']}'. "
            f"**Change Number:** {form_data['change_number']}",
        )

        st.balloons()
        st.snow()
        next_steps = get_cached_help_content("pop-next-steps")
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
    """Handle successful form submission."""
    # Show success message directly
    _create_success_callback(form_data)()

    # Reset form state
    _reset_deploy_pop_form_state()


def _reset_deploy_pop_form_state() -> None:
    """Reset the deploy PoP form state."""
    # Reset form fields
    for key in ["pop_name", "change_number", "location", "design", "provider"]:
        if key in st.session_state:
            del st.session_state[key]


def deploy_pop_form() -> None:
    """Streamlit form for deploying a PoP (Point of Presence)."""
    st.subheader("Deploy Point of Presence (PoP)")

    # Form instructions
    instructions = get_cached_help_content("deploy-pop-instructions")
    st.markdown(f"📋 {instructions}")

    with st.form("deploy_point_of_presence_form"):
        form_data = get_pop_form_data()

        submit_pop = st.form_submit_button("🚀 Submit PoP Request", use_container_width=True)

        if submit_pop:
            form_state = DeployPopFormState(**form_data)
            errors = validate_pop_form(form_state)

            if errors:
                _handle_validation_errors(errors)
            else:
                _handle_successful_submission(form_data)
