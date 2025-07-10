"""Unit tests for validation functions."""

from src.validation import (
    collect_validation_errors,
    validate_ip_subnet,
    validate_ip_subnet_optional,
    validate_minimum_count,
    validate_required_field,
    validate_required_selection,
    validate_unique_names,
)


class TestValidateRequiredField:
    """Test validate_required_field function."""

    def test_valid_field(self):
        """Test that valid field returns None."""
        result = validate_required_field("valid_value", "Test Field")
        assert result is None

    def test_empty_field(self):
        """Test that empty field returns error message."""
        result = validate_required_field("", "Test Field")
        assert result == "Test Field is required."

    def test_whitespace_only_field(self):
        """Test that whitespace-only field returns error message."""
        result = validate_required_field("   ", "Test Field")
        assert result == "Test Field is required."

    def test_none_field(self):
        """Test that None field returns error message."""
        result = validate_required_field(None, "Test Field")
        assert result == "Test Field is required."


class TestValidateRequiredSelection:
    """Test validate_required_selection function."""

    def test_valid_selection(self):
        """Test that valid selection returns None."""
        options = ["option1", "option2", "option3"]
        result = validate_required_selection(options, "option1", "Test Selection")
        assert result is None

    def test_no_selection_with_options(self):
        """Test that no selection with available options returns error."""
        options = ["option1", "option2", "option3"]
        result = validate_required_selection(options, "", "Test Selection")
        assert result == "Test Selection is required."

    def test_no_selection_no_options(self):
        """Test that no selection with no options returns None."""
        options = []
        result = validate_required_selection(options, "", "Test Selection")
        assert result is None

    def test_invalid_selection(self):
        """Test that invalid selection returns error."""
        options = ["option1", "option2", "option3"]
        result = validate_required_selection(options, "invalid", "Test Selection")
        assert result == "Test Selection is required."


class TestValidateMinimumCount:
    """Test validate_minimum_count function."""

    def test_sufficient_count(self):
        """Test that sufficient count returns None."""
        items = ["item1", "item2", "item3"]
        result = validate_minimum_count(items, 2, "test item")
        assert result is None

    def test_insufficient_count(self):
        """Test that insufficient count returns error."""
        items = ["item1"]
        result = validate_minimum_count(items, 2, "test item")
        assert result == "At least 2 test items are required."

    def test_exact_count(self):
        """Test that exact count returns None."""
        items = ["item1", "item2"]
        result = validate_minimum_count(items, 2, "test item")
        assert result is None

    def test_empty_list(self):
        """Test that empty list with minimum count returns error."""
        items = []
        result = validate_minimum_count(items, 1, "test item")
        assert result == "At least 1 test item is required."


class TestValidateUniqueNames:
    """Test validate_unique_names function."""

    def test_unique_names(self):
        """Test that unique names return None."""
        names = ["name1", "name2", "name3"]
        result = validate_unique_names(names, "Test Name")
        assert result is None

    def test_duplicate_names(self):
        """Test that duplicate names return error."""
        names = ["name1", "name2", "name1"]
        result = validate_unique_names(names, "Test Name")
        assert result == "Test Names must be unique. Duplicates found: name1"

    def test_multiple_duplicates(self):
        """Test that multiple duplicate names return error."""
        names = ["name1", "name2", "name1", "name2", "name3"]
        result = validate_unique_names(names, "Test Name")
        assert "Test Names must be unique. Duplicates found:" in result
        assert "name1" in result
        assert "name2" in result

    def test_empty_names_ignored(self):
        """Test that empty names are ignored in uniqueness check."""
        names = ["name1", "", "name2", ""]
        result = validate_unique_names(names, "Test Name")
        assert result is None


class TestCollectValidationErrors:
    """Test collect_validation_errors function."""

    def test_no_errors(self):
        """Test that no errors returns empty list."""
        result = collect_validation_errors(None, None, None)
        assert result == []

    def test_single_error(self):
        """Test that single error returns list with one item."""
        result = collect_validation_errors("Error 1", None, None)
        assert result == ["Error 1"]

    def test_multiple_errors(self):
        """Test that multiple errors returns list with all items."""
        result = collect_validation_errors("Error 1", "Error 2", "Error 3")
        assert result == ["Error 1", "Error 2", "Error 3"]

    def test_mixed_errors_and_none(self):
        """Test that mixed errors and None values work correctly."""
        result = collect_validation_errors("Error 1", None, "Error 3", None)
        assert result == ["Error 1", "Error 3"]

    def test_empty_string_ignored(self):
        """Test that empty strings are ignored."""
        result = collect_validation_errors("Error 1", "", "Error 3")
        assert result == ["Error 1", "Error 3"]


class TestValidateIpSubnet:
    """Test cases for validate_ip_subnet function."""

    def test_valid_ipv4_subnet(self):
        """Test that valid IPv4 subnets pass validation."""
        result = validate_ip_subnet("192.168.1.0/24", "Customer Subnet")
        assert result is None

    def test_valid_ipv6_subnet(self):
        """Test that valid IPv6 subnets pass validation."""
        result = validate_ip_subnet("2001:db8::/32", "Customer Subnet")
        assert result is None

    def test_empty_subnet(self):
        """Test that empty subnet fails validation."""
        result = validate_ip_subnet("", "Customer Subnet")
        assert result == "Customer Subnet is required"

    def test_none_subnet(self):
        """Test that None subnet fails validation."""
        result = validate_ip_subnet(None, "Customer Subnet")
        assert result == "Customer Subnet is required"

    def test_invalid_subnet(self):
        """Test that invalid subnet fails validation."""
        result = validate_ip_subnet("invalid", "Customer Subnet")
        assert result == "Customer Subnet must be a valid IP subnet (e.g., 192.168.1.0/24)"

    def test_whitespace_only_subnet(self):
        """Test that whitespace-only subnet fails validation."""
        result = validate_ip_subnet("   ", "Customer Subnet")
        assert result == "Customer Subnet is required"

    def test_subnet_with_whitespace(self):
        """Test that subnet with surrounding whitespace passes validation."""
        result = validate_ip_subnet("  192.168.1.0/24  ", "Customer Subnet")
        assert result is None


class TestValidateIpSubnetOptional:
    """Test cases for validate_ip_subnet_optional function."""

    def test_valid_ipv4_subnet(self):
        """Test that valid IPv4 subnets pass validation."""
        result = validate_ip_subnet_optional("192.168.1.0/24", "Public Subnet")
        assert result is None

    def test_empty_subnet(self):
        """Test that empty subnet passes validation (optional)."""
        result = validate_ip_subnet_optional("", "Public Subnet")
        assert result is None

    def test_none_subnet(self):
        """Test that None subnet passes validation (optional)."""
        result = validate_ip_subnet_optional(None, "Public Subnet")
        assert result is None

    def test_invalid_subnet(self):
        """Test that invalid subnet fails validation."""
        result = validate_ip_subnet_optional("invalid", "Public Subnet")
        assert result == "Public Subnet must be a valid IP subnet (e.g., 192.168.1.0/24)"

    def test_whitespace_only_subnet(self):
        """Test that whitespace-only subnet passes validation (optional)."""
        result = validate_ip_subnet_optional("   ", "Public Subnet")
        assert result is None
