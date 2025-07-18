# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Device connection service module."""

from typing import NamedTuple

import streamlit as st

from schema_protocols import DcimDeviceType, LocationBuilding
from utils import (
    get_dynamic_list,
    handle_validation_errors,
    init_dynamic_field_state,
    select_options,
    show_help_section,
    update_dynamic_field_state,
)
from validation import (
    collect_validation_errors,
    validate_minimum_count,
    validate_required_field,
    validate_unique_names,
    validate_vpc_groups,
)

INTERFACE_SPEEDS = ["1 Gbit", "10 Gbit", "40 Gbit", "100 Gbit"]
INTERFACE_ROLES = ["data", "management"]


def _initialize_dynamic_fields() -> None:
    for field in ["iface_name", "iface_speed", "iface_role", "iface_vpc_group"]:
        init_dynamic_field_state(
            field, default_value="none" if field == "iface_vpc_group" else ""
        )


def _update_dynamic_fields() -> None:
    for field in ["iface_name", "iface_speed", "iface_role", "iface_vpc_group"]:
        update_dynamic_field_state(field)


class DeviceConnectionState(NamedTuple):
    """Represents the state of a device connection form."""

    change_number: str
    device_name: str
    device_type: str
    location: str
    num_interfaces: int
    num_vpc_groups: int
    interface_names: list[str]
    interface_speeds: list[str]
    interface_roles: list[str]
    vpc_groups: list[str]


def validate_device_connection(state: DeviceConnectionState) -> list[str]:
    """Validate device connection form fields and return a list of error messages.

    Args:
        state: The current state of the device connection form.

    Returns:
        list[str]: A list of error messages, empty if no errors are found.

    """
    filtered_vpc_groups = [g if g != "none" else "" for g in state.vpc_groups]
    vpc_group_errors = validate_vpc_groups(
        [g != "none" for g in state.vpc_groups], filtered_vpc_groups
    )
    vpc_error = None
    if vpc_group_errors:
        vpc_error = f"Each vPC group must have at least two interfaces. Invalid groups: {', '.join(vpc_group_errors)}"
    return collect_validation_errors(
        validate_required_field(state.change_number, "Change number"),
        validate_required_field(state.device_name, "Device name"),
        validate_minimum_count(state.interface_names, 1, "interface with a name"),
        validate_unique_names(state.interface_names, "Interface names"),
        vpc_error,
    )


def interface_summary(state: DeviceConnectionState) -> str:
    """Generate a summary of interface configuration.

    Returns:
        str: A comma-separated summary string of interface configurations.

    """
    return ", ".join(
        f"{name} ({speed}, {role}" + (f", vPC {vpc}" if vpc != "none" else "") + ")"
        for name, speed, role, vpc in zip(
            state.interface_names,
            state.interface_speeds,
            state.interface_roles,
            state.vpc_groups,
            strict=False,
        )
    )


def render_device_connection_form() -> tuple[DeviceConnectionState | None, bool]:
    """Render the simplified device connection form.

    Returns:
        tuple[DeviceConnectionState | None, bool]: The state of the device connection
        form and a boolean indicating if the form was submitted.

    """
    with st.form("device_connection_form", border=False):
        change_number = st.session_state.get("change_number")
        device_name = st.session_state.get("device_name")
        device_type = st.session_state.get("device_type")
        location = st.session_state.get("location")
        num_interfaces = int(st.session_state.get("num_interfaces_planning", 1))
        num_vpc_groups = int(st.session_state.get("num_vpc_groups_planning", 0))
        _initialize_dynamic_fields()
        vpc_group_options = ["none"] + [
            f"vPC-{i + 1}" for i in range(int(num_vpc_groups))
        ]
        interface_names = get_dynamic_list("iface_name", "", int(num_interfaces))
        interface_speeds = get_dynamic_list(
            "iface_speed", INTERFACE_SPEEDS[0], int(num_interfaces)
        )
        interface_roles = get_dynamic_list(
            "iface_role", INTERFACE_ROLES[0], int(num_interfaces)
        )
        vpc_groups = get_dynamic_list("iface_vpc_group", "none", int(num_interfaces))
        st.markdown("**Configure Interfaces:**")
        for i in range(int(num_interfaces)):
            cols = st.columns([2, 2, 2, 2])
            interface_names[i] = cols[0].text_input(
                f"Interface Name {i + 1} *",
                value=interface_names[i],
                key=f"iface_name_{i}",
                help=f"Enter name for interface {i + 1}",
            )
            interface_speeds[i] = cols[1].selectbox(
                "Speed",
                INTERFACE_SPEEDS,
                index=(
                    INTERFACE_SPEEDS.index(interface_speeds[i])
                    if interface_speeds[i] in INTERFACE_SPEEDS
                    else 0
                ),
                key=f"iface_speed_{i}",
                help="Select the interface speed.",
            )
            interface_roles[i] = cols[2].selectbox(
                "Role",
                INTERFACE_ROLES,
                index=(
                    INTERFACE_ROLES.index(interface_roles[i])
                    if interface_roles[i] in INTERFACE_ROLES
                    else 0
                ),
                key=f"iface_role_{i}",
                help="Choose interface role.",
            )
            vpc_groups[i] = cols[3].selectbox(
                "vPC Group",
                vpc_group_options,
                index=(
                    vpc_group_options.index(vpc_groups[i])
                    if vpc_groups[i] in vpc_group_options
                    else 0
                ),
                key=f"iface_vpc_group_{i}",
                help="Assign to vPC group or select 'none'.",
            )
        submit = st.form_submit_button(
            "🚀 Submit Device Connection",
            use_container_width=True,
            help="Submit your device connection request.",
        )
        if submit:
            state = DeviceConnectionState(
                change_number=change_number,
                device_name=device_name,
                device_type=device_type,
                location=location,
                num_interfaces=int(num_interfaces),
                num_vpc_groups=int(num_vpc_groups),
                interface_names=interface_names,
                interface_speeds=interface_speeds,
                interface_roles=interface_roles,
                vpc_groups=vpc_groups,
            )
            return state, True
        return None, False


def deploy_network_form() -> None:
    """Streamlit form for device connection and interface configuration."""
    st.subheader("Device Connection Request")
    show_help_section(
        "Deployment Instructions", "connect-device-instructions", icon="📋"
    )
    # Interface configuration controls with callback outside the form
    st.markdown("**🔧 Interface Planning:**")
    st.text_input(
        "Change Number *",
        key="change_number",
        help="Enter the change management number for this connection request. This is required for tracking and approval.",
        placeholder="e.g., CHG-2024-001234",
    )

    st.text_input(
        "Device Name *",
        key="device_name",
        help="Enter a unique name for the device. Use a descriptive name that includes location "
        "and purpose (e.g., 'NYC-Core-SW01', 'LAB-Router-A')",
        placeholder="e.g., NYC-Core-SW01",
    )

    st.selectbox(
        "Device type *",
        select_options(DcimDeviceType),
        key="device_type",
        help="Choose the device type.",
    )

    st.selectbox(
        "Device type *",
        select_options(LocationBuilding),
        key="location",
        help="Choose the device location.",
    )

    cols_iface = st.columns([2, 2])
    cols_iface[0].number_input(
        "Number of Interfaces",
        min_value=1,
        step=1,
        key="num_interfaces_planning",
        on_change=_update_dynamic_fields,
        help="Total number of network interfaces to configure.",
    )
    cols_iface[1].number_input(
        "Number of vPC Groups",
        min_value=0,
        max_value=int(st.session_state.get("num_interfaces_planning", 1)),
        value=0,
        step=1,
        key="num_vpc_groups_planning",
        on_change=_update_dynamic_fields,
        help="Number of virtual port channel groups for redundancy.",
    )
    # vPC group information
    num_vpc_groups = int(st.session_state.get("num_vpc_groups_planning", 0))
    if num_vpc_groups > 0:
        st.info(
            f"💡 You have {num_vpc_groups} vPC groups configured. "
            f"Remember to assign at least 2 interfaces to each group.",
        )
    st.markdown("<div style='margin:0.5rem 0'></div>", unsafe_allow_html=True)
    # Initialize dynamic fields
    _initialize_dynamic_fields()
    # Render main form
    state, submitted = render_device_connection_form()
    if submitted and state:
        errors = validate_device_connection(state)
        if errors:
            handle_validation_errors(errors)
        else:
            st.success(
                f"✅ **Success!** Connection request for '{state.device_name}' "
                f"({state.device_type}) at '{state.location}' has been submitted. "
                f"**Change Number:** {state.change_number}",
            )
            st.balloons()
            st.snow()
            st.markdown(f"**Configured Interfaces:** {interface_summary(state)}")
            show_help_section("Next Steps", "connection-next-steps")
