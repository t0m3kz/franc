# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Kafka integration module for the FRANC Service Portal.

Publishes service requests as events to Kafka topics for downstream processing.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import streamlit as st
from kafka import KafkaProducer
from pydantic import BaseModel, Field


# Data classes for parameter grouping
@dataclass
class DeviceConnectionRequest:
    """Data class for device connection request parameters."""

    change_number: str
    device_name: str
    device_type: str
    location: str
    interfaces: list[dict[str, Any]]
    vpc_groups: list[str] | None = None
    user_id: str | None = None


@dataclass
class DeploymentRequest:
    """Data class for deployment request parameters."""

    change_number: str
    name: str
    location: str
    design_pattern: str
    user_id: str | None = None


@dataclass
class PopDeploymentRequest:
    """Data class for PoP deployment request parameters."""

    change_number: str
    name: str
    location: str
    design_pattern: str
    provider: str
    user_id: str | None = None


@dataclass
class TaskStatusRequest:
    """Data class for task status update parameters."""

    original_request_id: str
    change_number: str
    status: str
    progress_percentage: int | None = None
    status_message: str | None = None
    error_details: str | None = None
    estimated_completion: datetime | None = None
    user_id: str | None = None


@dataclass
class TaskCompletionRequest:
    """Data class for task completion parameters."""

    original_request_id: str
    change_number: str
    completion_status: str
    completion_message: str | None = None
    result_data: dict[str, Any] | None = None
    error_details: str | None = None
    execution_duration: float | None = None
    user_id: str | None = None


# Event Models
class ServiceRequestEvent(BaseModel):
    """Base model for service request events."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of service request")
    change_number: str = Field(..., description="Change management number")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    user_id: str | None = Field(None, description="User who submitted the request")
    source: str = Field(default="franc-portal", description="Source system")


class DeviceConnectionEvent(ServiceRequestEvent):
    """Device connection request event."""

    event_type: str = Field(default="device_connection", description="Event type")
    device_name: str = Field(..., description="Device name")
    device_type: str = Field(..., description="Device type")
    location: str = Field(..., description="Device location")
    interfaces: list[dict[str, Any]] = Field(..., description="Interface configurations")
    vpc_groups: list[str] | None = Field(None, description="vPC group configurations")


class DataCenterDeploymentEvent(ServiceRequestEvent):
    """Data center deployment request event."""

    event_type: str = Field(default="datacenter_deployment", description="Event type")
    dc_name: str = Field(..., description="Data center name")
    location: str = Field(..., description="Data center location")
    design_pattern: str = Field(..., description="Design pattern")


class PopDeploymentEvent(ServiceRequestEvent):
    """PoP deployment request event."""

    event_type: str = Field(default="pop_deployment", description="Event type")
    pop_name: str = Field(..., description="PoP name")
    location: str = Field(..., description="PoP location")
    design_pattern: str = Field(..., description="Design pattern")
    provider: str = Field(..., description="Service provider")


# Additional Event Models for Status Updates
class TaskStatusUpdateEvent(ServiceRequestEvent):
    """Task status update event."""

    event_type: str = Field(default="task_status_update", description="Event type")
    original_request_id: str = Field(..., description="Original request ID being updated")
    status: str = Field(..., description="Current task status: pending, in_progress, completed, failed")
    progress_percentage: int | None = Field(None, description="Progress percentage (0-100)")
    status_message: str | None = Field(None, description="Human-readable status message")
    error_details: str | None = Field(None, description="Error details if status is failed")
    estimated_completion: datetime | None = Field(None, description="Estimated completion time")


class TaskCompletionEvent(ServiceRequestEvent):
    """Task completion event."""

    event_type: str = Field(default="task_completion", description="Event type")
    original_request_id: str = Field(..., description="Original request ID that completed")
    completion_status: str = Field(..., description="Final status: completed, failed, cancelled")
    completion_message: str | None = Field(None, description="Completion summary message")
    result_data: dict[str, Any] | None = Field(None, description="Result data from completed task")
    error_details: str | None = Field(None, description="Error details if failed")
    execution_duration: float | None = Field(None, description="Task execution time in seconds")


class KafkaConfig:
    """Kafka configuration from environment variables."""

    def __init__(self) -> None:
        """Initialize Kafka configuration from environment variables."""
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic_prefix = os.getenv("KAFKA_TOPIC_PREFIX", "franc")
        self.security_protocol = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
        self.sasl_mechanism = os.getenv("KAFKA_SASL_MECHANISM")
        self.sasl_username = os.getenv("KAFKA_SASL_USERNAME")
        self.sasl_password = os.getenv("KAFKA_SASL_PASSWORD")
        self.ssl_cafile = os.getenv("KAFKA_SSL_CAFILE")
        self.ssl_certfile = os.getenv("KAFKA_SSL_CERTFILE")
        self.ssl_keyfile = os.getenv("KAFKA_SSL_KEYFILE")

    def get_producer_config(self) -> dict[str, Any]:
        """Get Kafka producer configuration.

        Returns:
            Dictionary containing Kafka producer configuration.

        """
        config = {
            "bootstrap_servers": self.bootstrap_servers.split(","),
            "value_serializer": lambda v: json.dumps(v, default=str).encode("utf-8"),
            "key_serializer": lambda k: k.encode("utf-8") if k else None,
            "acks": "all",  # Wait for all replicas to acknowledge
            "retries": 3,
            "retry_backoff_ms": 1000,
        }

        if self.security_protocol != "PLAINTEXT":
            config["security_protocol"] = self.security_protocol

        if self.sasl_mechanism:
            config["sasl_mechanism"] = self.sasl_mechanism
            config["sasl_plain_username"] = self.sasl_username
            config["sasl_plain_password"] = self.sasl_password

        if self.ssl_cafile:
            config["ssl_cafile"] = self.ssl_cafile
            config["ssl_certfile"] = self.ssl_certfile
            config["ssl_keyfile"] = self.ssl_keyfile

        return config


class EventPublisher:
    """Publishes service request events to Kafka."""

    def __init__(self, config: KafkaConfig | None = None) -> None:
        """Initialize EventPublisher with optional Kafka configuration.

        Args:
            config: Optional Kafka configuration. If None, uses default configuration.

        """
        self.config = config or KafkaConfig()
        self.logger = logging.getLogger(__name__)
        self._producer: KafkaProducer | None = None

    @property
    def producer(self) -> KafkaProducer:
        """Get or create Kafka producer."""
        if self._producer is None:
            try:
                self._producer = KafkaProducer(**self.config.get_producer_config())
                self.logger.info("Kafka producer initialized successfully")
            except Exception:
                self.logger.exception("Failed to initialize Kafka producer")
                raise
        return self._producer

    def publish_event(self, event: ServiceRequestEvent, topic_suffix: str = "requests") -> bool:
        """Publish a service request event to Kafka.

        Args:
            event: The service request event to publish
            topic_suffix: Suffix for the Kafka topic (default: "requests")

        Returns:
            True if successful, False otherwise

        """
        topic = f"{self.config.topic_prefix}.{topic_suffix}"

        try:
            # Convert Pydantic model to dict
            event_data = event.model_dump()

            # Use change number as the message key for partitioning
            key = event.change_number

            # Send to Kafka
            future = self.producer.send(topic, value=event_data, key=key)

            # Block until message is sent (for reliability)
            record_metadata = future.get(timeout=10)
        except (ConnectionError, TimeoutError, ValueError):
            self.logger.exception("Failed to publish event to Kafka")
            return False
        else:
            self.logger.info(
                "Published %s event to %s (partition: %d, offset: %d)",
                event.event_type,
                topic,
                record_metadata.partition,
                record_metadata.offset,
            )
            return True

    def close(self) -> None:
        """Close the Kafka producer."""
        if self._producer:
            self._producer.flush()
            self._producer.close()
            self._producer = None


class _EventPublisherSingleton:
    """Singleton wrapper for EventPublisher."""

    _instance: EventPublisher | None = None

    @classmethod
    def get_instance(cls) -> EventPublisher:
        """Get the singleton event publisher instance.

        Returns:
            The singleton EventPublisher instance.

        """
        if cls._instance is None:
            cls._instance = EventPublisher()
        return cls._instance


def get_event_publisher() -> EventPublisher:
    """Get the event publisher instance.

    Returns:
        The singleton EventPublisher instance.

    """
    return _EventPublisherSingleton.get_instance()


def _create_device_connection_event(request: DeviceConnectionRequest) -> DeviceConnectionEvent:
    """Create a device connection event.

    Returns:
        DeviceConnectionEvent instance for the request.

    """
    return DeviceConnectionEvent(
        event_id=f"conn_{request.change_number}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        change_number=request.change_number,
        request_id=f"device_conn_{request.change_number}",
        device_name=request.device_name,
        device_type=request.device_type,
        location=request.location,
        interfaces=request.interfaces,
        vpc_groups=request.vpc_groups,
        user_id=request.user_id,
    )


def publish_device_connection_event(request: DeviceConnectionRequest) -> bool:
    """Publish a device connection request event.

    Args:
        request: Device connection request data

    Returns:
        True if successful, False otherwise

    """
    event = _create_device_connection_event(request)

    try:
        publisher = get_event_publisher()
        return publisher.publish_event(event, "device.connection")
    except (ConnectionError, TimeoutError, ValueError, OSError) as e:
        st.error(f"Failed to publish device connection event: {e}")
        return False


def _create_datacenter_deployment_event(request: DeploymentRequest) -> DataCenterDeploymentEvent:
    """Create a data center deployment event.

    Returns:
        DataCenterDeploymentEvent instance for the request.

    """
    return DataCenterDeploymentEvent(
        event_id=f"dc_{request.change_number}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        change_number=request.change_number,
        request_id=f"datacenter_{request.change_number}",
        dc_name=request.name,
        location=request.location,
        design_pattern=request.design_pattern,
        user_id=request.user_id,
    )


def publish_datacenter_deployment_event(
    change_number: str,
    dc_name: str,
    location: str,
    design_pattern: str,
    user_id: str | None = None,
) -> bool:
    """Publish a data center deployment request event.

    Args:
        change_number: Change management number
        dc_name: Data center name
        location: Data center location
        design_pattern: Design pattern
        user_id: Optional user identifier

    Returns:
        True if successful, False otherwise

    """
    request = DeploymentRequest(
        change_number=change_number,
        name=dc_name,
        location=location,
        design_pattern=design_pattern,
        user_id=user_id,
    )

    event = _create_datacenter_deployment_event(request)

    try:
        publisher = get_event_publisher()
        return publisher.publish_event(event, "datacenter.deployment")
    except (ConnectionError, TimeoutError, ValueError, OSError) as e:
        st.error(f"Failed to publish data center deployment event: {e}")
        return False


def _create_pop_deployment_event(request: PopDeploymentRequest) -> PopDeploymentEvent:
    """Create a PoP deployment event.

    Returns:
        PopDeploymentEvent instance for the request.

    """
    return PopDeploymentEvent(
        event_id=f"pop_{request.change_number}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        change_number=request.change_number,
        request_id=f"pop_{request.change_number}",
        pop_name=request.name,
        location=request.location,
        design_pattern=request.design_pattern,
        provider=request.provider,
        user_id=request.user_id,
    )


def publish_pop_deployment_event(request: PopDeploymentRequest) -> bool:
    """Publish a PoP deployment request event.

    Args:
        request: PoP deployment request data

    Returns:
        True if successful, False otherwise

    """
    event = _create_pop_deployment_event(request)

    try:
        publisher = get_event_publisher()
        return publisher.publish_event(event, "pop.deployment")
    except (ConnectionError, TimeoutError, ValueError, OSError) as e:
        st.error(f"Failed to publish PoP deployment event: {e}")
        return False


def publish_task_status_update(request: TaskStatusRequest) -> bool:
    """Publish a task status update event.

    Args:
        request: Task status update request data

    Returns:
        True if successful, False otherwise

    """
    event = TaskStatusUpdateEvent(
        event_id=f"status_{request.change_number}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        change_number=request.change_number,
        request_id=f"status_update_{request.change_number}",
        original_request_id=request.original_request_id,
        status=request.status,
        progress_percentage=request.progress_percentage,
        status_message=request.status_message,
        error_details=request.error_details,
        estimated_completion=request.estimated_completion,
        user_id=request.user_id,
    )

    try:
        publisher = get_event_publisher()
        return publisher.publish_event(event, "task.status")
    except (ConnectionError, TimeoutError, ValueError, OSError) as e:
        st.error(f"Failed to publish task status update: {e}")
        return False


def publish_task_completion(request: TaskCompletionRequest) -> bool:
    """Publish a task completion event.

    Args:
        request: Task completion request data

    Returns:
        True if successful, False otherwise

    """
    event = TaskCompletionEvent(
        event_id=f"complete_{request.change_number}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        change_number=request.change_number,
        request_id=f"completion_{request.change_number}",
        original_request_id=request.original_request_id,
        completion_status=request.completion_status,
        completion_message=request.completion_message,
        result_data=request.result_data,
        error_details=request.error_details,
        execution_duration=request.execution_duration,
        user_id=request.user_id,
    )

    try:
        publisher = get_event_publisher()
        return publisher.publish_event(event, "task.completion")
    except (ConnectionError, TimeoutError, ValueError, OSError) as e:
        st.error(f"Failed to publish task completion event: {e}")
        return False


def is_kafka_enabled() -> bool:
    """Check if Kafka integration is enabled.

    Returns:
        bool: True if Kafka is enabled, False otherwise.

    """
    return os.getenv("KAFKA_ENABLED", "false").lower() in {"true", "1", "yes", "on"}


def test_kafka_connection() -> bool:
    """Test Kafka connection and return status.

    Returns:
        bool: True if Kafka connection is successful, False otherwise.

    """
    if not is_kafka_enabled():
        return False

    logger = logging.getLogger(__name__)
    try:
        publisher = get_event_publisher()
        # Try to get metadata (this will test the connection)
        producer = publisher.producer
        producer.list_topics(timeout=5)
    except (ConnectionError, TimeoutError, ValueError, OSError):
        logger.exception("Kafka connection test failed")
        return False
    else:
        return True
