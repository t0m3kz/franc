# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Data center deployment service module."""

from typing import Any, NamedTuple

import streamlit as st

from help_loader import get_cached_help_content
from schema_protocols import DesignTopology, IpamPrefix, LocationMetro, OrganizationProvider, TopologyDataCenter
from utils import (
    CreateObjectConfig,
    create_and_save_object,
    create_deployment_branch,
    dropdown_options,
    select_options,
)
from validation import (
    collect_validation_errors,
    validate_ip_subnet,
    validate_ip_subnet_optional,
    validate_required_field,
    validate_required_selection,
)


class DeployDcFormState(NamedTuple):
    """State container for datacenter deployment form data."""

    change_number: str
    dc_name: str
    description: str
    location_options: list[Any]
    location: str
    design_options: list[Any]
    design: str
    strategy_options: list[Any]
    strategy: str
    provider_options: list[Any]
    provider: str
    customer_subnet: str
    management_subnet: str
    technical_subnet: str
    public_subnet: str


def validate_data_center_form(state: DeployDcFormState) -> list[str]:
    """Validate Data Center deployment form fields and return a list of error messages.

    Returns:
        list[str]: List of validation error messages.

    """
    return collect_validation_errors(
        validate_required_field(state.change_number, "Change Number"),
        validate_required_field(state.dc_name, "Data Center Name"),
        validate_required_selection(
            [opt["id"] for opt in state.location_options] if state.location_options else [], state.location, "Location"
        ),
        validate_required_selection(
            [opt["id"] for opt in state.design_options] if state.design_options else [], state.design, "Design Pattern"
        ),
        validate_required_selection(state.strategy_options, state.strategy, "Strategy"),
        validate_required_selection(
            [opt["id"] for opt in state.provider_options] if state.provider_options else [], state.provider, "Provider"
        ),
        validate_ip_subnet(state.customer_subnet, "Customer Subnet"),
        validate_ip_subnet(state.management_subnet, "Management Subnet"),
        validate_ip_subnet(state.technical_subnet, "Technical Subnet"),
        validate_ip_subnet_optional(state.public_subnet, "Public Subnet"),
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

    dc_name = st.text_input(
        "Data Center Name *",
        key="dc_name",
        help="Enter a unique name for the data center. Use a descriptive name that includes "
        "location or purpose (e.g., 'NYC-Main-DC', 'London-Edge-01'). This name must be unique across all data centers.",
        placeholder="e.g., NYC-Main-DC",
    )

    description = st.text_area(
        "Description",
        key="dc_description",
        help="Optional description of the data center's purpose, capacity, or special characteristics.",
        placeholder="e.g., Primary data center for East Coast operations with high availability requirements",
    )

    # Location selection
    location_options = select_options(LocationMetro)
    if location_options:
        # Create a mapping for display
        location_labels = [opt["label"] for opt in location_options]
        location_mapping = {opt["label"]: opt["id"] for opt in location_options}

        selected_location_label = st.selectbox(
            "Location *",
            location_labels,
            key="dc_location",
            help="Select the metro area where the data center will be deployed. This determines network connectivity and regional settings.",
        )
        location = location_mapping.get(selected_location_label)
    else:
        location = st.text_input(
            "Location * (Manual Entry)",
            key="dc_location_manual",
            help="Enter the metro area manually. Contact support if location options are not loading.",
            placeholder="e.g., New York, London, Tokyo",
        )
        st.info("💡 Location options are not available. Using manual entry mode.")

    # Design pattern selection
    design_options = select_options(DesignTopology, filters={"type__value": "DC"})
    if design_options:
        # Create a mapping for display
        design_labels = [opt["label"] for opt in design_options]
        design_mapping = {opt["label"]: opt["id"] for opt in design_options}

        selected_design_label = st.selectbox(
            "Design Pattern *",
            design_labels,
            key="dc_design",
            help="Choose the infrastructure design template. Different patterns provide varying levels of redundancy, capacity, and features.",
        )
        design = design_mapping.get(selected_design_label)
    else:
        design = st.text_input(
            "Design Pattern * (Manual Entry)",
            key="dc_design_manual",
            help="Enter the design pattern manually. Common patterns: 'Standard', 'High-Availability', 'Edge'.",
            placeholder="e.g., Standard, High-Availability",
        )
        st.info("💡 Design pattern options are not available. Using manual entry mode.")

    # Strategy selection
    strategy_options = dropdown_options(TopologyDataCenter, attribute_name="strategy")
    if strategy_options:
        strategy = st.selectbox(
            "Strategy *",
            strategy_options,
            key="dc_strategy",
            help="Select the deployment strategy. This affects how the data center is provisioned and configured.",
        )
    else:
        strategy = st.text_input(
            "Strategy * (Manual Entry)",
            key="dc_strategy_manual",
            help="Enter the deployment strategy manually. Common strategies: 'Greenfield', 'Brownfield', 'Hybrid'.",
            placeholder="e.g., Greenfield, Brownfield, Hybrid",
        )
        st.info("💡 Strategy options are not available. Using manual entry mode.")

    # Provider selection
    provider_options = select_options(OrganizationProvider)
    if provider_options:
        # Create a mapping for display
        provider_labels = [opt["label"] for opt in provider_options]
        provider_mapping = {opt["label"]: opt["id"] for opt in provider_options}

        selected_provider_label = st.selectbox(
            "Provider *",
            provider_labels,
            key="dc_provider",
            help="Select the service provider for this data center. This determines billing, support, and operational responsibilities.",
        )
        provider = provider_mapping.get(selected_provider_label)
    else:
        provider = st.text_input(
            "Provider * (Manual Entry)",
            key="dc_provider_manual",
            help="Enter the provider name manually. This should be the organization responsible for the data center.",
            placeholder="e.g., AWS, Azure, Internal",
        )
        st.info("💡 Provider options are not available. Using manual entry mode.")

    # Subnet configuration
    st.subheader("Subnet Configuration")

    customer_subnet = st.text_input(
        "Customer Subnet *",
        key="dc_customer_subnet",
        help="Enter the IP subnet for customer-facing services (e.g., 192.168.1.0/24). This subnet will be used for customer connectivity.",
        placeholder="e.g., 192.168.1.0/24",
    )

    management_subnet = st.text_input(
        "Management Subnet *",
        key="dc_management_subnet",
        help="Enter the IP subnet for management services (e.g., 10.0.0.0/24). This subnet is used for device management and monitoring.",
        placeholder="e.g., 10.0.0.0/24",
    )

    technical_subnet = st.text_input(
        "Technical Subnet *",
        key="dc_technical_subnet",
        help="Enter the IP subnet for technical/operational services (e.g., 10.0.1.0/24). This subnet is used for internal technical operations.",
        placeholder="e.g., 10.0.1.0/24",
    )

    public_subnet = st.text_input(
        "Public Subnet",
        key="dc_public_subnet",
        help="Optional IP subnet for public-facing services (e.g., 203.0.113.0/24). Leave empty if not needed.",
        placeholder="e.g., 203.0.113.0/24",
    )

    return {
        "change_number": change_number,
        "dc_name": dc_name,
        "description": description,
        "location_options": location_options,
        "location": location,
        "design_options": design_options,
        "design": design,
        "strategy_options": strategy_options,
        "strategy": strategy,
        "provider_options": provider_options,
        "provider": provider,
        "customer_subnet": customer_subnet,
        "management_subnet": management_subnet,
        "technical_subnet": technical_subnet,
        "public_subnet": public_subnet,
    }


def _show_success_message(form_data: dict[str, Any]) -> None:
    """Display DC deployment success message.

    Args:
        form_data: The validated form data containing DC configuration

    """
    st.success(f"✅ **Data Center '{form_data['dc_name']}' deployment submitted successfully!**")
    st.success("✅ **Data Center object created with all subnet relationships established in Infrahub!**")

    # Display configuration summary
    st.info("📋 **Configuration Summary:**")
    st.write(f"• **Change Number:** {form_data['change_number']}")
    st.write(f"• **Name:** {form_data['dc_name']}")
    if form_data.get("description"):
        st.write(f"• **Description:** {form_data['description']}")
    st.write(f"• **Location:** {form_data['location']}")
    st.write(f"• **Design:** {form_data['design']}")
    st.write(f"• **Strategy:** {form_data['strategy']}")
    st.write(f"• **Provider:** {form_data['provider']}")

    # Show created objects with relationships
    st.info("🏢 **Created Objects with Relationships:**")
    st.write(f"• **Data Center:** {form_data['dc_name']} (with linked subnets)")
    st.write(f"• **Customer Subnet:** {form_data['customer_subnet']} → linked to DC")
    st.write(f"• **Management Subnet:** {form_data['management_subnet']} → linked to DC")
    st.write(f"• **Technical Subnet:** {form_data['technical_subnet']} → linked to DC")
    if form_data.get("public_subnet"):
        st.write(f"• **Public Subnet:** {form_data['public_subnet']} → linked to DC")

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
    """Handle successful form submission with branch creation and object creation."""
    branch_name = f"implement_{form_data.get('change_number', '').lower()}"

    # Create deployment branch using the global utility function
    success = create_deployment_branch(branch_name)

    # Create objects if branch creation succeeded
    if success:
        objects_created = _create_dc_objects(form_data, branch_name)

        if objects_created:
            _show_success_message(form_data)
        else:
            st.error("❌ **Branch created but object creation failed.** Please check the configuration and try again.")
    else:
        st.error("❌ **Deployment failed.** Branch creation was unsuccessful.")


def _create_dc_objects(form_data: dict[str, Any], branch_name: str) -> bool:
    """Create all objects in Infrahub for the data center deployment.

    Args:
        form_data: The validated form data containing deployment information
        branch_name: The branch name to create the objects in

    Returns:
        bool: True if all objects were created successfully, False otherwise

    """
    # Create customer subnet prefix
    customer_subnet_data = {
        "prefix": form_data["customer_subnet"],
        "description": f"Customer subnet for DC {form_data['dc_name']}",
        "status": "active",
        "role": "server",  # Use 'server' role for customer-facing services
    }

    config = CreateObjectConfig(object_name="Customer Subnet")
    customer_prefix = create_and_save_object(
        kind=IpamPrefix,
        data=customer_subnet_data,
        branch=branch_name,
        config=config,
    )

    if not customer_prefix:
        return False

    # Create management subnet prefix
    management_subnet_data = {
        "prefix": form_data["management_subnet"],
        "description": f"Management subnet for DC {form_data['dc_name']}",
        "status": "active",
        "role": "management",
    }

    config = CreateObjectConfig(object_name="Management Subnet")
    management_prefix = create_and_save_object(
        kind=IpamPrefix,
        data=management_subnet_data,
        branch=branch_name,
        config=config,
    )

    if not management_prefix:
        return False

    # Create technical subnet prefix
    technical_subnet_data = {
        "prefix": form_data["technical_subnet"],
        "description": f"Technical/operational subnet for DC {form_data['dc_name']}",
        "status": "active",
        "role": "technical",  # This role is valid according to the error message
    }

    config = CreateObjectConfig(object_name="Technical Subnet")
    technical_prefix = create_and_save_object(
        kind=IpamPrefix,
        data=technical_subnet_data,
        branch=branch_name,
        config=config,
    )

    if not technical_prefix:
        return False

    # Create public subnet prefix if provided
    public_prefix = None
    if form_data.get("public_subnet"):
        public_subnet_data = {
            "prefix": form_data["public_subnet"],
            "description": f"Public subnet for DC {form_data['dc_name']}",
            "status": "active",
            "role": "public",
        }

        config = CreateObjectConfig(object_name="Public Subnet")
        public_prefix = create_and_save_object(
            kind=IpamPrefix,
            data=public_subnet_data,
            branch=branch_name,
            config=config,
        )

        if not public_prefix:
            return False

    # Create the TopologyDataCenter object with relationships to created prefixes
    dc_data = {
        "name": form_data["dc_name"],
        "description": form_data.get("description", ""),
        "strategy": form_data["strategy"],
        "customer_subnet": customer_prefix,
        "management_subnet": management_prefix,
        "technical_subnet": technical_prefix,
    }

    # Add public subnet reference if it was created
    if public_prefix:
        dc_data["public_subnet"] = public_prefix

    # Add location, design, and provider references if they are available as valid IDs
    if form_data.get("location") and form_data["location_options"]:
        # Location is now an ID from the dropdown selection
        dc_data["location"] = form_data["location"]

    if form_data.get("design") and form_data["design_options"]:
        # Design is now an ID from the dropdown selection
        dc_data["design"] = form_data["design"]

    if form_data.get("provider") and form_data["provider_options"]:
        # Provider is now an ID from the dropdown selection
        dc_data["provider"] = form_data["provider"]

    config = CreateObjectConfig(object_name="Data Center")
    data_center = create_and_save_object(
        kind=TopologyDataCenter,
        data=dc_data,
        branch=branch_name,
        config=config,
    )

    return bool(data_center)


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
