# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Unit tests for Kafka integration module."""

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.kafka_integration import (
    DeploymentRequest,
    DeviceConnectionEvent,
    DeviceConnectionRequest,
    PopDeploymentRequest,
    ServiceRequestEvent,
    TaskCompletionRequest,
    TaskStatusRequest,
    get_event_publisher,
    is_kafka_enabled,
)


class TestServiceRequestEvent:
    """Test ServiceRequestEvent model."""

    def test_create_service_request_event(self):
        """Test creating a basic service request event."""
        event = ServiceRequestEvent(
            event_id="test-123",
            event_type="test_request",
            change_number="CHG-001",
            request_id="req-456",
        )

        assert event.event_id == "test-123"
        assert event.event_type == "test_request"
        assert event.change_number == "CHG-001"
        assert event.request_id == "req-456"
        assert event.source == "franc-portal"
        assert isinstance(event.timestamp, datetime)

    def test_service_request_event_with_user_id(self):
        """Test creating service request event with user ID."""
        event = ServiceRequestEvent(
            event_id="test-123",
            event_type="test_request",
            change_number="CHG-001",
            request_id="req-456",
            user_id="user123",
        )

        assert event.user_id == "user123"


class TestDeviceConnectionEvent:
    """Test DeviceConnectionEvent model."""

    def test_create_device_connection_event(self):
        """Test creating a device connection event."""
        interfaces = [{"name": "eth0", "speed": "1 Gbit", "role": "data"}]

        event = DeviceConnectionEvent(
            event_id="device-123",
            event_type="device_connection",
            change_number="CHG-002",
            request_id="req-789",
            device_name="test-device",
            device_type="router",
            location="datacenter-1",
            interfaces=interfaces,
        )

        assert event.device_name == "test-device"
        assert event.device_type == "router"
        assert event.location == "datacenter-1"
        assert event.interfaces == interfaces
        assert event.vpc_groups is None

    def test_device_connection_event_with_vpc_groups(self):
        """Test creating device connection event with VPC groups."""
        interfaces = [{"name": "eth0", "speed": "1 Gbit", "role": "data"}]
        vpc_groups = ["vpc-group-1", "vpc-group-2"]

        event = DeviceConnectionEvent(
            event_id="device-123",
            event_type="device_connection",
            change_number="CHG-002",
            request_id="req-789",
            device_name="test-device",
            device_type="router",
            location="datacenter-1",
            interfaces=interfaces,
            vpc_groups=vpc_groups,
        )

        assert event.vpc_groups == vpc_groups


class TestDataClasses:
    """Test data classes for parameter grouping."""

    def test_device_connection_request(self):
        """Test DeviceConnectionRequest data class."""
        interfaces = [{"name": "eth0", "speed": "1 Gbit", "role": "data"}]

        request = DeviceConnectionRequest(
            change_number="CHG-003",
            device_name="test-router",
            device_type="router",
            location="dc-west",
            interfaces=interfaces,
            vpc_groups=["vpc-1"],
            user_id="admin",
        )

        assert request.change_number == "CHG-003"
        assert request.device_name == "test-router"
        assert request.device_type == "router"
        assert request.location == "dc-west"
        assert request.interfaces == interfaces
        assert request.vpc_groups == ["vpc-1"]
        assert request.user_id == "admin"

    def test_deployment_request(self):
        """Test DeploymentRequest data class."""
        request = DeploymentRequest(
            change_number="CHG-004",
            name="test-deployment",
            location="dc-east",
            design_pattern="standard",
            user_id="operator",
        )

        assert request.change_number == "CHG-004"
        assert request.name == "test-deployment"
        assert request.location == "dc-east"
        assert request.design_pattern == "standard"
        assert request.user_id == "operator"

    def test_pop_deployment_request(self):
        """Test PopDeploymentRequest data class."""
        request = PopDeploymentRequest(
            change_number="CHG-005",
            name="pop-deployment",
            location="edge-1",
            design_pattern="edge",
            provider="provider-a",
            user_id="engineer",
        )

        assert request.change_number == "CHG-005"
        assert request.name == "pop-deployment"
        assert request.location == "edge-1"
        assert request.design_pattern == "edge"
        assert request.provider == "provider-a"
        assert request.user_id == "engineer"

    def test_task_status_request(self):
        """Test TaskStatusRequest data class."""
        completion_time = datetime.now(timezone.utc)

        request = TaskStatusRequest(
            original_request_id="req-123",
            change_number="CHG-006",
            status="in_progress",
            progress_percentage=50,
            status_message="Processing deployment",
            estimated_completion=completion_time,
        )

        assert request.original_request_id == "req-123"
        assert request.change_number == "CHG-006"
        assert request.status == "in_progress"
        assert request.progress_percentage == 50
        assert request.status_message == "Processing deployment"
        assert request.estimated_completion == completion_time

    def test_task_completion_request(self):
        """Test TaskCompletionRequest data class."""
        result_data = {"deployed_items": 5, "success_rate": 100.0}

        request = TaskCompletionRequest(
            original_request_id="req-456",
            change_number="CHG-007",
            completion_status="success",
            completion_message="Deployment completed successfully",
            result_data=result_data,
            execution_duration=120.5,
        )

        assert request.original_request_id == "req-456"
        assert request.change_number == "CHG-007"
        assert request.completion_status == "success"
        assert request.completion_message == "Deployment completed successfully"
        assert request.result_data == result_data
        assert request.execution_duration == 120.5


class TestEventPublisher:
    """Test EventPublisher class and related functions."""

    @patch.dict(
        os.environ,
        {
            "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
            "KAFKA_TOPIC_PREFIX": "test-franc",
        },
    )
    @patch("src.kafka_integration.KafkaProducer")
    def test_event_publisher_initialization(self, mock_producer):
        """Test EventPublisher initialization with valid config."""
        mock_producer_instance = MagicMock()
        mock_producer.return_value = mock_producer_instance

        publisher = get_event_publisher()

        assert publisher is not None
        # Access the producer property to trigger initialization
        _ = publisher.producer
        mock_producer.assert_called_once()

    def test_is_kafka_enabled_function(self):
        """Test the is_kafka_enabled function with various values."""
        # Test with different true values
        for true_value in ["true", "1", "yes", "on", "True", "TRUE"]:
            with patch.dict(os.environ, {"KAFKA_ENABLED": true_value}):
                assert is_kafka_enabled() is True

        # Test with different false values
        for false_value in ["false", "0", "no", "off", "False", "FALSE", ""]:
            with patch.dict(os.environ, {"KAFKA_ENABLED": false_value}):
                assert is_kafka_enabled() is False

        # Test with missing env var
        with patch.dict(os.environ, {}, clear=True):
            assert is_kafka_enabled() is False

    def test_is_kafka_enabled_true(self):
        """Test is_kafka_enabled returns True for valid values."""
        with patch.dict(os.environ, {"KAFKA_ENABLED": "true"}):
            assert is_kafka_enabled() is True

        with patch.dict(os.environ, {"KAFKA_ENABLED": "1"}):
            assert is_kafka_enabled() is True

        with patch.dict(os.environ, {"KAFKA_ENABLED": "yes"}):
            assert is_kafka_enabled() is True

    def test_is_kafka_enabled_false(self):
        """Test is_kafka_enabled returns False for invalid or missing values."""
        with patch.dict(os.environ, {"KAFKA_ENABLED": "false"}):
            assert is_kafka_enabled() is False

        with patch.dict(os.environ, {}, clear=True):
            assert is_kafka_enabled() is False
