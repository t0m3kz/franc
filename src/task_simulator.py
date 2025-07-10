# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Task execution simulation module for the FRANC Service Portal.

Simulates task execution with status updates and completion events.
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import streamlit as st

from kafka_integration import is_kafka_enabled, publish_task_completion, publish_task_status_update


class TaskSimulator:
    """Simulates task execution with status updates."""

    def __init__(self, task_name: str, change_number: str, request_id: str) -> None:
        """Initialize task simulator with task details.

        Args:
            task_name: Name of the task being simulated
            change_number: Change management number
            request_id: Unique request identifier

        """
        self.task_name = task_name
        self.change_number = change_number
        self.request_id = request_id
        self.start_time = time.time()

    def simulate_task_execution(self, steps: list[dict[str, Any]]) -> bool:
        """Simulate task execution with progress updates.

        Args:
            steps: List of task steps with 'name', 'duration', and optional 'failure_chance'

        Returns:
            True if task completed successfully, False if failed

        """
        if not is_kafka_enabled():
            # If Kafka is disabled, just show a quick completion message
            st.info(f"✅ Task simulation completed: {self.task_name}")
            return True

        # Create progress bar and status container
        progress_bar = st.progress(0)
        status_container = st.empty()

        # Publish initial status
        self._publish_status_update(
            status="in_progress",
            progress_percentage=0,
            status_message=f"Starting {self.task_name}...",
        )

        total_steps = len(steps)

        try:
            for i, step in enumerate(steps):
                step_name = step["name"]
                duration = step.get("duration", 2)  # Default 2 seconds
                failure_chance = step.get("failure_chance", 0.0)  # Default no failure

                # Update status
                progress_percentage = int((i / total_steps) * 100)
                status_container.write(f"🔄 **Step {i + 1}/{total_steps}:** {step_name}")
                progress_bar.progress(progress_percentage)

                # Publish status update
                self._publish_status_update(
                    status="in_progress",
                    progress_percentage=progress_percentage,
                    status_message=f"Executing: {step_name}",
                    estimated_completion=datetime.now(timezone.utc) + timedelta(seconds=(total_steps - i) * 2),
                )

                # Simulate work
                time.sleep(duration)

                # Simulate potential failure
                if failure_chance > 0 and time.time() % 10 < failure_chance:
                    error_message = f"Failed during step: {step_name}"
                    status_container.error(f"❌ {error_message}")

                    # Publish failure status
                    self._publish_status_update(
                        status="failed",
                        progress_percentage=progress_percentage,
                        status_message=f"Task failed at step: {step_name}",
                        error_details=error_message,
                    )

                    # Publish completion event
                    self._publish_completion_event(
                        completion_status="failed",
                        completion_message=f"Task failed during {step_name}",
                        error_details=error_message,
                    )

                    return False

        except (OSError, ValueError, KeyError) as e:
            # Handle expected errors
            status_container.error(f"❌ **Unexpected error:** {e!s}")

            # Publish failure status
            self._publish_status_update(
                status="failed",
                progress_percentage=0,
                status_message=f"Unexpected error during {self.task_name}",
                error_details=str(e),
            )

            # Publish completion event
            self._publish_completion_event(
                completion_status="failed",
                completion_message="Task failed due to unexpected error",
                error_details=str(e),
            )

            return False
        else:
            # Task completed successfully
            progress_bar.progress(100)
            status_container.success(f"✅ **Completed:** {self.task_name}")

            # Publish final status update
            self._publish_status_update(
                status="completed",
                progress_percentage=100,
                status_message=f"Task completed successfully: {self.task_name}",
            )

            # Publish completion event
            self._publish_completion_event(
                completion_status="completed",
                completion_message=f"Task completed successfully: {self.task_name}",
                result_data={"steps_completed": total_steps, "execution_time": time.time() - self.start_time},
            )

            return True

    def _publish_status_update(
        self,
        status: str,
        progress_percentage: int,
        status_message: str,
        error_details: str | None = None,
        estimated_completion: datetime | None = None,
    ) -> None:
        """Publish a task status update event."""
        if is_kafka_enabled():
            publish_task_status_update(
                original_request_id=self.request_id,
                change_number=self.change_number,
                status=status,
                progress_percentage=progress_percentage,
                status_message=status_message,
                error_details=error_details,
                estimated_completion=estimated_completion,
            )

    def _publish_completion_event(
        self,
        completion_status: str,
        completion_message: str,
        result_data: dict[str, Any] | None = None,
        error_details: str | None = None,
    ) -> None:
        """Publish a task completion event."""
        if is_kafka_enabled():
            execution_duration = time.time() - self.start_time
            publish_task_completion(
                original_request_id=self.request_id,
                change_number=self.change_number,
                completion_status=completion_status,
                completion_message=completion_message,
                result_data=result_data,
                error_details=error_details,
                execution_duration=execution_duration,
            )


def simulate_device_connection_task(device_name: str, change_number: str, interface_count: int) -> bool:
    """Simulate device connection task execution.

    Returns:
        bool: True if the simulation completes successfully, False otherwise.

    """
    request_id = f"device_conn_{change_number}"
    simulator = TaskSimulator(f"Device Connection: {device_name}", change_number, request_id)

    steps = [
        {"name": "Validating device connectivity", "duration": 1.5},
        {"name": "Backing up current configuration", "duration": 2.0},
        {"name": "Configuring management interface", "duration": 1.8},
        {"name": f"Configuring {interface_count} data interfaces", "duration": 2.5},
        {"name": "Applying vPC configurations", "duration": 2.2},
        {"name": "Verifying connectivity", "duration": 1.5},
        {"name": "Running post-deployment tests", "duration": 2.0},
    ]

    return simulator.simulate_task_execution(steps)


def simulate_datacenter_deployment_task(dc_name: str, change_number: str, design_pattern: str) -> bool:
    """Simulate data center deployment task execution.

    Returns:
        bool: True if the simulation completes successfully, False otherwise.

    """
    request_id = f"datacenter_{change_number}"
    simulator = TaskSimulator(f"Data Center Deployment: {dc_name}", change_number, request_id)

    steps = [
        {"name": "Validating deployment parameters", "duration": 1.0},
        {"name": "Provisioning spine switches", "duration": 3.0},
        {"name": "Provisioning leaf switches", "duration": 2.5},
        {"name": "Configuring underlay network", "duration": 2.8},
        {"name": "Configuring overlay network", "duration": 3.2},
        {"name": f"Applying {design_pattern} design pattern", "duration": 2.5},
        {"name": "Running connectivity tests", "duration": 2.0},
        {"name": "Validating redundancy", "duration": 1.8},
        {"name": "Generating deployment report", "duration": 1.2},
    ]

    return simulator.simulate_task_execution(steps)


def simulate_pop_deployment_task(pop_name: str, change_number: str, provider: str) -> bool:
    """Simulate PoP deployment task execution.

    Returns:
        bool: True if the simulation completes successfully, False otherwise.

    """
    request_id = f"pop_{change_number}"
    simulator = TaskSimulator(f"PoP Deployment: {pop_name}", change_number, request_id)

    steps = [
        {"name": "Coordinating with provider", "duration": 2.0},
        {"name": f"Provisioning {provider} infrastructure", "duration": 3.5},
        {"name": "Installing edge devices", "duration": 2.8},
        {"name": "Configuring routing protocols", "duration": 2.5},
        {"name": "Establishing provider connections", "duration": 3.0},
        {"name": "Testing end-to-end connectivity", "duration": 2.2},
        {"name": "Validating SLA requirements", "duration": 1.8},
        {"name": "Updating network documentation", "duration": 1.5},
    ]

    return simulator.simulate_task_execution(steps)
