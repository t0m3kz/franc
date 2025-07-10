# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Global Kafka Events Helper for FRANC Service Portal.

Provides unified interface for publishing service events and handling workflows.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, TypedDict, Unpack

import streamlit as st

from kafka_integration import (
    is_kafka_enabled,
    publish_datacenter_deployment_event,
    publish_device_connection_event,
    publish_pop_deployment_event,
)
from task_simulator import (
    simulate_datacenter_deployment_task,
    simulate_device_connection_task,
    simulate_pop_deployment_task,
)


class DeviceTaskKwargs(TypedDict, total=False):
    """Type definition for device connection task kwargs."""

    device_name: str
    interface_count: int


class DatacenterTaskKwargs(TypedDict, total=False):
    """Type definition for datacenter deployment task kwargs."""

    dc_name: str
    design_pattern: str


class PopTaskKwargs(TypedDict, total=False):
    """Type definition for POP deployment task kwargs."""

    pop_name: str
    provider: str


# Union type for all task kwargs
TaskKwargs = DeviceTaskKwargs | DatacenterTaskKwargs | PopTaskKwargs


class ServiceType(Enum):
    """Enumeration of supported service types."""

    DEVICE_CONNECTION = "device_connection"
    DATACENTER_DEPLOYMENT = "datacenter_deployment"
    POP_DEPLOYMENT = "pop_deployment"


@dataclass
class DeviceConnectionEventData:
    """Device connection event data."""

    change_number: str
    device_name: str
    device_type: str
    location: str
    interfaces: list[dict[str, Any]]
    vpc_groups: list[str] | None = None
    user_id: str | None = None


@dataclass
class DatacenterDeploymentEventData:
    """Datacenter deployment event data."""

    change_number: str
    dc_name: str
    location: str
    design_pattern: str
    user_id: str | None = None


@dataclass
class PopDeploymentEventData:
    """PoP deployment event data."""

    change_number: str
    pop_name: str
    location: str
    design_pattern: str
    provider: str
    user_id: str | None = None


@dataclass
class TaskExecutionData:
    """Data required for task execution simulation."""

    service_name: str
    change_number: str
    # Additional fields can be added as needed for different service types


@dataclass
class KafkaEventResult:
    """Result of Kafka event publishing."""

    success: bool
    message: str
    should_execute_task: bool


class KafkaEventManager:
    """Central manager for Kafka events and service workflows."""

    # Mapping of service types to their event publishers
    _EVENT_PUBLISHERS: ClassVar[dict[ServiceType, Callable[..., bool]]] = {
        ServiceType.DEVICE_CONNECTION: publish_device_connection_event,
        ServiceType.DATACENTER_DEPLOYMENT: publish_datacenter_deployment_event,
        ServiceType.POP_DEPLOYMENT: publish_pop_deployment_event,
    }

    # Mapping of service types to their task simulators
    _TASK_SIMULATORS: ClassVar[dict[ServiceType, Callable[..., bool]]] = {
        ServiceType.DEVICE_CONNECTION: simulate_device_connection_task,
        ServiceType.DATACENTER_DEPLOYMENT: simulate_datacenter_deployment_task,
        ServiceType.POP_DEPLOYMENT: simulate_pop_deployment_task,
    }

    @staticmethod
    def publish_service_event(
        service_type: ServiceType,
        event_data: DeviceConnectionEventData | DatacenterDeploymentEventData | PopDeploymentEventData,
    ) -> KafkaEventResult:
        """Publish a service event to Kafka and return the result.

        Args:
            service_type: Type of service event
            event_data: Event data specific to the service
            **kwargs: Additional arguments for the specific publisher

        Returns:
            KafkaEventResult with success status and message

        """
        if not is_kafka_enabled():
            return KafkaEventResult(
                success=True,
                message="Kafka is disabled - events will not be published",
                should_execute_task=True,
            )

        # Get the appropriate publisher
        publisher = KafkaEventManager._EVENT_PUBLISHERS.get(service_type)
        if not publisher:
            return KafkaEventResult(
                success=False,
                message=f"No publisher found for service type: {service_type}",
                should_execute_task=False,
            )

        try:
            # Call the specific publisher with the event data
            if service_type == ServiceType.DEVICE_CONNECTION:
                data = event_data
                success = publisher(
                    change_number=data.change_number,
                    device_name=data.device_name,
                    device_type=data.device_type,
                    location=data.location,
                    interfaces=data.interfaces,
                    vpc_groups=data.vpc_groups,
                    user_id=data.user_id,
                )
            elif service_type == ServiceType.DATACENTER_DEPLOYMENT:
                data = event_data
                success = publisher(
                    change_number=data.change_number,
                    dc_name=data.dc_name,
                    location=data.location,
                    design_pattern=data.design_pattern,
                    user_id=data.user_id,
                )
            elif service_type == ServiceType.POP_DEPLOYMENT:
                data = event_data
                success = publisher(
                    change_number=data.change_number,
                    pop_name=data.pop_name,
                    location=data.location,
                    design_pattern=data.design_pattern,
                    provider=data.provider,
                    user_id=data.user_id,
                )
            else:
                success = False

            if success:
                return KafkaEventResult(
                    success=True,
                    message="📡 Event successfully published to Kafka for downstream processing.",
                    should_execute_task=True,
                )

            return KafkaEventResult(
                success=False,
                message="⚠️ Request submitted successfully, but failed to publish event to Kafka. Manual follow-up may be required.",
                should_execute_task=True,  # Still allow task execution
            )

        except (ConnectionError, TimeoutError, ValueError) as e:
            return KafkaEventResult(
                success=False,
                message=f"⚠️ Kafka event publishing failed: {e!s}. Manual follow-up may be required.",
                should_execute_task=True,  # Still allow task execution
            )

    @staticmethod
    def execute_task_simulation(
        service_type: ServiceType,
        task_data: TaskExecutionData,
        **kwargs: Unpack[TaskKwargs],
    ) -> bool:
        """Execute task simulation for the given service type.

        Args:
            service_type: Type of service
            task_data: Task execution data
            **kwargs: Additional arguments for the specific simulator

        Returns:
            True if task completed successfully, False otherwise

        """
        simulator = KafkaEventManager._TASK_SIMULATORS.get(service_type)
        if not simulator:
            st.error(f"❌ No task simulator found for service type: {service_type}")
            return False

        try:
            # Call the specific task simulator
            if service_type == ServiceType.DEVICE_CONNECTION:
                return simulator(
                    device_name=kwargs.get("device_name", task_data.service_name),
                    change_number=task_data.change_number,
                    interface_count=kwargs.get("interface_count", 1),
                )
            if service_type == ServiceType.DATACENTER_DEPLOYMENT:
                return simulator(
                    dc_name=kwargs.get("dc_name", task_data.service_name),
                    change_number=task_data.change_number,
                    design_pattern=kwargs.get("design_pattern", "Standard"),
                )
            if service_type == ServiceType.POP_DEPLOYMENT:
                return simulator(
                    pop_name=kwargs.get("pop_name", task_data.service_name),
                    change_number=task_data.change_number,
                    provider=kwargs.get("provider", "Unknown"),
                )

        except (ConnectionError, TimeoutError, ValueError) as e:
            st.error(f"❌ Task simulation failed: {e!s}")
            return False
        else:
            st.error(f"❌ Unsupported service type for task simulation: {service_type}")
            return False

    @staticmethod
    def handle_service_workflow(
        service_type: ServiceType,
        event_data: DeviceConnectionEventData | DatacenterDeploymentEventData | PopDeploymentEventData,
        task_data: TaskExecutionData,
        success_callback: Callable[[], None] | None = None,
        **task_kwargs: Unpack[TaskKwargs],
    ) -> None:
        """Handle the complete service workflow: event publishing + task execution.

        Args:
            service_type: Type of service
            event_data: Event data for Kafka publishing
            task_data: Task data for simulation
            success_callback: Optional callback to run after successful event publishing
            **task_kwargs: Additional arguments for task simulation

        """
        # Step 1: Publish Kafka event
        event_result = KafkaEventManager.publish_service_event(service_type, event_data)

        # Step 2: Show Kafka status if enabled
        if is_kafka_enabled():
            if event_result.success:
                st.info(event_result.message)
            else:
                st.warning(event_result.message)

        # Step 3: Run success callback (e.g., show success message, balloons)
        if success_callback:
            success_callback()

        # Step 4: Execute task simulation if appropriate
        if event_result.should_execute_task:
            st.markdown("---")
            st.markdown("### 🔄 Task Execution")

            task_success = KafkaEventManager.execute_task_simulation(service_type, task_data, **task_kwargs)

            if task_success:
                st.success("🎉 **Task completed successfully!** Service deployment is now active.")
            else:
                st.error("❌ **Task failed.** Please check the error details above and retry if needed.")


# Convenience functions for each service type
def handle_device_connection_workflow(
    event_data: DeviceConnectionEventData,
    task_data: TaskExecutionData,
    success_callback: Callable[[], None] | None = None,
) -> None:
    """Handle complete device connection workflow."""
    KafkaEventManager.handle_service_workflow(
        ServiceType.DEVICE_CONNECTION,
        event_data,
        task_data,
        success_callback,
        device_name=event_data.device_name,
        interface_count=len(event_data.interfaces),
    )


def handle_datacenter_deployment_workflow(
    event_data: DatacenterDeploymentEventData,
    task_data: TaskExecutionData,
    success_callback: Callable[[], None] | None = None,
) -> None:
    """Handle complete datacenter deployment workflow."""
    KafkaEventManager.handle_service_workflow(
        ServiceType.DATACENTER_DEPLOYMENT,
        event_data,
        task_data,
        success_callback,
        dc_name=event_data.dc_name,
        design_pattern=event_data.design_pattern,
    )


def handle_pop_deployment_workflow(
    event_data: PopDeploymentEventData,
    task_data: TaskExecutionData,
    success_callback: Callable[[], None] | None = None,
) -> None:
    """Handle complete PoP deployment workflow."""
    KafkaEventManager.handle_service_workflow(
        ServiceType.POP_DEPLOYMENT,
        event_data,
        task_data,
        success_callback,
        pop_name=event_data.pop_name,
        provider=event_data.provider,
    )
