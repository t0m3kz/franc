# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Simple unit tests for basic data structures."""

from dataclasses import dataclass


class TestDataStructures:
    """Test basic data structure creation and manipulation."""

    def test_basic_dataclass_creation(self):
        """Test creating and using basic dataclasses."""
        @dataclass
        class TestDevice:
            display_name: str
            id: str
            hostname: str

        device = TestDevice("Test Device", "device-123", "test.example.com")

        assert device.display_name == "Test Device"
        assert device.id == "device-123"
        assert device.hostname == "test.example.com"

    def test_dataclass_with_optional_fields(self):
        """Test dataclass with optional fields."""
        @dataclass
        class TestInterface:
            display_name: str
            id: str
            name: str
            description: str = ""

        interface = TestInterface("eth0", "int-123", "ethernet0")

        assert interface.display_name == "eth0"
        assert interface.id == "int-123"
        assert interface.name == "ethernet0"
        assert not interface.description

        # Test with description
        interface_with_desc = TestInterface("eth1", "int-456", "ethernet1", "Management Interface")
        assert interface_with_desc.description == "Management Interface"

    def test_attribute_types(self):
        """Test that attributes have the correct types."""
        @dataclass
        class TestLocation:
            display_name: str
            id: str

        location = TestLocation("Data Center 1", "loc-789")

        assert isinstance(location.display_name, str)
        assert isinstance(location.id, str)
        assert len(location.display_name) > 0
        assert len(location.id) > 0

    def test_dataclass_equality(self):
        """Test dataclass equality comparison."""
        @dataclass
        class TestItem:
            name: str
            value: int

        item1 = TestItem("test", 42)
        item2 = TestItem("test", 42)
        item3 = TestItem("different", 42)

        assert item1 == item2
        assert item1 != item3
        assert item2 != item3

    def test_dataclass_representation(self):
        """Test dataclass string representation."""
        @dataclass
        class TestPattern:
            display_name: str
            id: str

        pattern = TestPattern("Standard Pattern", "pattern-001")

        # Test that repr contains the class name and field values
        repr_str = repr(pattern)
        assert "TestPattern" in repr_str
        assert "Standard Pattern" in repr_str
        assert "pattern-001" in repr_str
