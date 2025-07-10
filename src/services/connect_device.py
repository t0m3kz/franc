# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Device connection service module."""

from typing import Any, NamedTuple

import streamlit as st

from help_loader import get_cached_help_content, show_help_section
from kafka_events_helper import (
    DeviceConnectionEventData,
    TaskExecutionData,
    handle_device_connection_workflow,
)
from schema_protocols import DcimDeviceType, LocationBuilding
from utils import (
    get_dynamic_list,
    init_dynamic_field_state,
    select_options,
    update_dynamic_field_state,
)
from validation import (
    collect_validation_errors,
    validate_minimum_count,
    validate_required_field,
    validate_unique_names,
    validate_vpc_groups,
)

# --- Constants ---
INTERFACE_SPEED_OPTIONS = ["1 Gbit", "10 Gbit", "40 Gbit", "100 Gbit"]
INTERFACE_ROLE_OPTIONS = ["data", "management"]

# --- Form state classes local to this service ---


class InterfaceFormState(NamedTuple):
    """State container for interface form data."""

    num: int
    names: list[str]
    speeds: list[str]
    roles: list[str]
    vpc_groups: list[str]


class ConnectDeviceFormState(NamedTuple):
    """State container for connect device form data."""

    change_number: str
    device_name: str
    device_type: str
    location: str
    interfaces: InterfaceFormState
    has_device_type_options: bool = False
    has_location_options: bool = False


def validate_connect_device_form(state: ConnectDeviceFormState) -> list[str]:
    """Validate connect device form fields and return a list of error messages.

    Returns:
        List of validation error messages.

    """
    # Prepare vPC validation
    filtered_vpc_groups = [g if g != "none" else "" for g in state.interfaces.vpc_groups]
    vpc_group_errors = validate_vpc_groups([g != "none" for g in state.interfaces.vpc_groups], filtered_vpc_groups)

    vpc_error = None
    if vpc_group_errors:
        vpc_error = f"Each vPC group must have at least two interfaces. Invalid groups: {', '.join(vpc_group_errors)}"

    return collect_validation_errors(
        validate_required_field(state.change_number, "Change number"),
        validate_required_field(state.device_name, "Device name"),
        validate_required_field(state.device_type, "Device type"),
        validate_required_field(state.location, "Location"),
        validate_minimum_count(state.interfaces.names, 1, "interface with a name"),
        validate_unique_names(state.interfaces.names, "Interface names"),
        vpc_error,
    )


def generate_interface_summary(iface_state: InterfaceFormState) -> str:
    """Generate a human-readable summary of interface configuration.

    Returns:
        str: A formatted string summarizing the interface configuration.

    """
    return ", ".join(
        f"{name} ({speed}, {role}" + (f", vPC {vpc}" if vpc != "none" else "") + ")"
        for name, speed, role, vpc in zip(
            iface_state.names,
            iface_state.speeds,
            iface_state.roles,
            iface_state.vpc_groups,
            strict=False,
        )
    )


def render_interfaces(num_interfaces: int, num_vpc_groups: int) -> InterfaceFormState:
    """Render interface fields and return interface state with user input.

    Returns:
        InterfaceFormState: The state containing all interface configuration data.

    """
    vpc_group_options = ["none"] + [f"vPC-{i + 1}" for i in range(num_vpc_groups)]

    # Interface configuration help
    show_help_section("Interface Configuration Help", "interface-config", "🔧")

    # Get current values from session state
    names = get_dynamic_list("iface_name", "", num_interfaces)
    speeds = get_dynamic_list("iface_speed", "1 Gbit", num_interfaces)
    roles = get_dynamic_list("iface_role", "data", num_interfaces)
    vpc_groups = get_dynamic_list("iface_vpc_group", "none", num_interfaces)

    # Render interface fields with enhanced labels
    st.markdown("**Configure Network Interfaces:**")
    for i in range(num_interfaces):
        st.markdown(f"**Interface {i + 1}:**")
        cols = st.columns([2, 2, 2, 2])
        names[i] = cols[0].text_input(
            "Name *",
            value=names[i],
            key=f"iface_name_{i}",
            help=f"Enter name for interface {i + 1} (e.g., Gi0/{i}, eth{i})",
        )
        speeds[i] = cols[1].selectbox(
            "Speed",
            INTERFACE_SPEED_OPTIONS,
            index=INTERFACE_SPEED_OPTIONS.index(speeds[i]) if speeds[i] in INTERFACE_SPEED_OPTIONS else 0,
            key=f"iface_speed_{i}",
            help="Select the interface speed/bandwidth",
        )
        roles[i] = cols[2].selectbox(
            "Role",
            INTERFACE_ROLE_OPTIONS,
            index=INTERFACE_ROLE_OPTIONS.index(roles[i]) if roles[i] in INTERFACE_ROLE_OPTIONS else 0,
            key=f"iface_role_{i}",
            help="Choose interface purpose: data (production) or management (admin)",
        )
        vpc_groups[i] = cols[3].selectbox(
            "vPC Group",
            vpc_group_options,
            index=vpc_group_options.index(vpc_groups[i]) if vpc_groups[i] in vpc_group_options else 0,
            key=f"iface_vpc_group_{i}",
            help="Assign to vPC group for redundancy, or select 'none' for standalone",
        )

    return InterfaceFormState(
        num=num_interfaces,
        names=names,
        speeds=speeds,
        roles=roles,
        vpc_groups=vpc_groups,
    )


def get_connect_device_form_data() -> dict[str, Any]:
    """Collect form input data for device connection.

    Returns:
        dict[str, Any]: A dictionary containing all form input data.

    """
    change_number = st.text_input(
        "Change Number *",
        key="conn_change_number",
        help="Enter the change management number for this connection request. This is required for tracking and approval.",
        placeholder="e.g., CHG-2024-001234",
    )

    conn_name = st.text_input(
        "Device Name *",
        key="conn_name",
        help="Enter a unique name for the device. Use a descriptive name that includes location "
        "and purpose (e.g., 'NYC-Core-SW01', 'LAB-Router-A')",
        placeholder="e.g., NYC-Core-SW01",
    )

    # Device type selection with fallback
    device_type_options = select_options(DcimDeviceType)
    if device_type_options:
        selected_device_type = st.selectbox(
            "Device Type *",
            options=device_type_options,
            key="conn_device_type",
            help="Select the type/role of device. This determines network policies and configuration templates.",
        )
    else:
        selected_device_type = st.text_input(
            "Device Type * (Manual Entry)",
            key="conn_device_type_manual",
            help="Enter the device type manually. Common types: 'Switch', 'Router', 'Firewall', 'Server'.",
            placeholder="e.g., Switch, Router, Firewall",
        )
        st.info("💡 Device type options are not available. Using manual entry mode.")

    # Location selection with fallback
    location_options = select_options(LocationBuilding)
    if location_options:
        selected_location = st.selectbox(
            "Location *",
            options=location_options,
            key="conn_location",
            help="Select the physical location where the device is installed. This affects network topology.",
        )
    else:
        selected_location = st.text_input(
            "Location * (Manual Entry)",
            key="conn_location_manual",
            help="Enter the location manually. Be specific about building, floor, or rack location.",
            placeholder="e.g., Building A Floor 2, Rack R15",
        )
        st.info("💡 Location options are not available. Using manual entry mode.")

    return {
        "change_number": change_number,
        "device_name": conn_name,
        "device_type": selected_device_type,
        "location": selected_location,
        "has_device_type_options": bool(device_type_options),
        "has_location_options": bool(location_options),
    }


def _initialize_dynamic_states() -> None:
    """Initialize all dynamic field states for interface form."""
    for field in ["iface_name", "iface_speed", "iface_role", "iface_vpc_group"]:
        init_dynamic_field_state(field, default_value="none" if field == "iface_vpc_group" else "")


def _update_all_dynamic_states() -> None:
    """Update all dynamic field states when interface count changes."""
    for field in ["iface_name", "iface_speed", "iface_role", "iface_vpc_group"]:
        update_dynamic_field_state(field)


def _prepare_interface_data(interfaces: InterfaceFormState) -> list[dict[str, Any]]:
    """Prepare interface data for Kafka event publishing.

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing interface data.

    """
    return [
        {
            "name": interfaces.names[i],
            "speed": interfaces.speeds[i],
            "role": interfaces.roles[i],
            "vpc_group": interfaces.vpc_groups[i] if interfaces.vpc_groups[i] != "none" else None,
        }
        for i in range(interfaces.num)
    ]


def _prepare_vpc_groups_data(interfaces: InterfaceFormState) -> list[str] | None:
    """Prepare vPC groups data for Kafka event publishing.

    Returns:
        list[str] | None: List of vPC group names or None if no vPC groups configured.

    """
    return (
        [g for g in interfaces.vpc_groups if g != "none"] if any(g != "none" for g in interfaces.vpc_groups) else None
    )


def _create_success_callback(form_state: ConnectDeviceFormState, interfaces: InterfaceFormState) -> callable:
    """Create a success callback function for the workflow.

    Returns:
        callable: A function that displays success message and interface summary.

    """

    def success_callback() -> None:
        summary = generate_interface_summary(interfaces)

        st.success(
            f"✅ **Success!** Connection request for '{form_state.device_name}' "
            f"({form_state.device_type}) at '{form_state.location}' has been submitted. "
            f"**Change Number:** {form_state.change_number}",
        )

        st.balloons()
        st.snow()
        st.markdown(f"**Configured Interfaces:** {summary}")

        next_steps = get_cached_help_content("connection-next-steps")
        st.markdown(next_steps)

    return success_callback


def _handle_validation_errors(errors: list[str]) -> None:
    """Handle and display validation errors."""
    st.error("❌ **Please fix the following issues:**")
    for err in errors:
        st.error(f"• {err}")
    validation_tips = get_cached_help_content("validation-tips")
    st.markdown(f"💡 {validation_tips}")


def _handle_successful_submission(form_state: ConnectDeviceFormState, interfaces: InterfaceFormState) -> None:
    """Handle successful form submission using the global Kafka events helper."""
    # Prepare interface and vPC data
    interface_data = _prepare_interface_data(interfaces)
    vpc_groups_data = _prepare_vpc_groups_data(interfaces)

    # Create success callback
    success_callback = _create_success_callback(form_state, interfaces)

    # Create event data
    event_data = DeviceConnectionEventData(
        change_number=form_state.change_number,
        device_name=form_state.device_name,
        device_type=form_state.device_type,
        location=form_state.location,
        interfaces=interface_data,
        vpc_groups=vpc_groups_data,
        user_id=None,  # Could be enhanced to include actual user ID
    )

    # Create task data
    task_data = TaskExecutionData(
        service_name=form_state.device_name,
        change_number=form_state.change_number,
    )

    # Use the global helper to handle the complete workflow
    handle_device_connection_workflow(
        event_data=event_data,
        task_data=task_data,
        success_callback=success_callback,
    )


def _render_interface_planning_controls() -> None:
    """Render interface planning controls section."""
    st.markdown("**🔧 Interface Planning:**")
    cols_iface = st.columns([2, 2])
    cols_iface[0].number_input(
        "Number of Interfaces",
        min_value=1,
        step=1,
        key="num_iface_name",
        on_change=_update_all_dynamic_states,
        help="Total number of network interfaces to configure for this device. "
        "Include both data and management interfaces.",
    )
    cols_iface[1].number_input(
        "Number of vPC Groups",
        min_value=0,
        max_value=int(st.session_state.get("num_iface_name", 1)),
        value=0,
        step=1,
        key="num_vpc_groups",
        help="Number of virtual port channel groups for redundancy. Each vPC group requires at least 2 interfaces.",
    )

    # vPC group information
    num_vpc_groups = int(st.session_state.get("num_vpc_groups", 0))
    if num_vpc_groups > 0:
        st.info(
            f"💡 You have {num_vpc_groups} vPC groups configured. "
            f"Remember to assign at least 2 interfaces to each group.",
        )

    st.markdown("<div style='margin:0.5rem 0'></div>", unsafe_allow_html=True)


def _render_main_form() -> tuple[ConnectDeviceFormState | None, bool]:
    """Render the main form and return form state and submission status.

    Returns:
        tuple[ConnectDeviceFormState | None, bool]: Form state and submission status.

    """
    with st.form("connect_device_form"):
        # Get form data
        num_interfaces = int(st.session_state.get("num_iface_name", 1))
        num_vpc_groups = int(st.session_state.get("num_vpc_groups", 0))

        # Render form sections
        device_info = get_connect_device_form_data()
        interfaces = render_interfaces(num_interfaces, num_vpc_groups)

        # Submit button
        submit_conn = st.form_submit_button(
            "🚀 Submit Connection Request",
            use_container_width=True,
            help="Submit your device connection request for processing",
        )

        if submit_conn:
            # Create form state
            form_state = ConnectDeviceFormState(
                change_number=device_info["change_number"],
                device_name=device_info["device_name"],
                device_type=device_info["device_type"],
                location=device_info["location"],
                interfaces=interfaces,
                has_device_type_options=device_info["has_device_type_options"],
                has_location_options=device_info["has_location_options"],
            )
            return form_state, True

        return None, False


def connect_device_form() -> None:
    """Streamlit form for connecting a device with interfaces."""
    st.subheader("Device Connection Request")

    # Form instructions
    instructions = get_cached_help_content("connect-device-instructions")
    st.markdown(f"📋 {instructions}")

    # Initialize dynamic states
    _initialize_dynamic_states()

    # Interface configuration controls
    _render_interface_planning_controls()

    # Render main form
    form_state, submitted = _render_main_form()

    # Handle form submission
    if submitted and form_state:
        errors = validate_connect_device_form(form_state)

        if errors:
            _handle_validation_errors(errors)
        else:
            # Here we can process infrahub update
            _handle_successful_submission(form_state, form_state.interfaces)
