# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""FRANC Service Portal main application."""

import streamlit as st

from help_loader import show_help_section
from services.connect_device import connect_device_form
from services.deploy_dc import deploy_dc_form
from services.deploy_pop import deploy_pop_form

st.set_page_config(page_title="Service Portal", layout="centered", page_icon="🛠️")


# Responsive mobile-friendly header
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
        <span style="font-size:2.2rem;">🛠️</span>
        <div>
            <h1 style="margin-bottom:0;font-size:1.7rem;">Service Portal</h1>
            <p style="margin-top:0; color: #888; font-size:1rem;">Network Operations Self-Service</p>
        </div>
    </div>
    <hr style='margin-top:0;margin-bottom:1.2rem;'>
    """,
    unsafe_allow_html=True,
)


# Mobile-friendly navigation: use a bottom nav bar style
tab_names = ["Home", "Service Catalogue"]
nav = st.columns(len(tab_names))
selected_tab = tab_names[0]
for i, name in enumerate(tab_names):
    if nav[i].button(name, use_container_width=True):
        st.session_state["main_tab"] = name
if "main_tab" in st.session_state:
    selected_tab = st.session_state["main_tab"]

if selected_tab == "Home":
    st.markdown(
        """
        <div style="padding:1.2rem 0 0.5rem 0;">
            <h2 style='font-size:1.3rem;'>Welcome to the Service Portal</h2>
            <p style='font-size:1rem;'>
                Use the navigation below to access network service requests.<br>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Service overview cards
    st.markdown("### 📋 Available Services")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            **🏢 Deploy Data Center**
            - Request new DC deployment
            - Select location and design
            - Automated provisioning
            """,
        )

    with col2:
        st.markdown(
            """
            **🌐 Deploy PoP**
            - Point of Presence setup
            - Provider selection
            - Geographic expansion
            """,
        )

    with col3:
        st.markdown(
            """
            **🔌 Connection Request**
            - Device network connection
            - Interface configuration
            - vPC group setup
            """,
        )

    # Quick help section
    show_help_section("Quick Help & Tips", "quick-help")
elif selected_tab == "Service Catalogue":
    st.markdown("<h2 style='margin-bottom:0.5rem;font-size:1.2rem;'>Service Catalogue</h2>", unsafe_allow_html=True)

    # Service descriptions
    st.markdown(
        """
        Select a service below to get started. Each service includes built-in help and validation
        to guide you through the process.
        """,
    )

    # Use a mobile-friendly selectbox for service selection
    service = st.selectbox(
        "Select a service:",
        ["Deploy Data Center", "Deploy PoP", "Connection Request"],
        key="service_select",
        help="Choose the network service you want to request. Each service has different requirements and workflows.",
    )

    # Service-specific help before showing the form
    if service == "Deploy Data Center":
        show_help_section("About Data Center Deployment", "deploy-dc")
        deploy_dc_form()
    elif service == "Connection Request":
        show_help_section("About Device Connection Requests", "connect-device")
        connect_device_form()
    elif service == "Deploy PoP":
        show_help_section("About Point of Presence Deployment", "deploy-pop")
        deploy_pop_form()
