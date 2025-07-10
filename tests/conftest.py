"""Pytest configuration and fixtures for FRANC tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_streamlit():
    """Mock streamlit module for testing."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    mock_st.info = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.expander = MagicMock()
    return mock_st


@pytest.fixture
def sample_form_data():
    """Sample form data for testing."""
    return {
        "change_number": "CHG-2024-001234",
        "device_name": "test-device-01",
        "device_type": "router",
        "location": "datacenter-01",
    }


@pytest.fixture
def sample_interface_data():
    """Sample interface data for testing."""
    return [
        {
            "name": "eth0",
            "speed": "1 Gbit",
            "role": "management",
            "vpc_group": None,
        },
        {
            "name": "eth1",
            "speed": "10 Gbit",
            "role": "data",
            "vpc_group": "vpc1",
        },
    ]
