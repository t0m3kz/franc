# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Workflow engine for multi-step Infrahub operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

import streamlit as st

if TYPE_CHECKING:
    from collections.abc import Callable


class WorkflowStep(NamedTuple):
    """Represents a single step in a workflow."""

    name: str
    function: Callable[..., Any]
    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None


class WorkflowResult(NamedTuple):
    """Result of workflow execution."""

    success_count: int
    total_steps: int
    error_count: int
    steps_results: list[dict[str, Any]]
    errors: list[dict[str, Any]]


class WorkflowEngine:
    """Engine for executing multi-step workflows with Infrahub integration."""

    def __init__(self, workflow_name: str) -> None:
        """Initialize workflow engine.

        Args:
            workflow_name: Display name for the workflow

        """
        self.workflow_name = workflow_name
        self.steps: list[WorkflowStep] = []

    def add_step(
        self,
        name: str,
        function: Callable[..., Any],
        *args: object,
        **kwargs: object,
    ) -> None:
        """Add a step to the workflow.

        Args:
            name: Display name for the step
            function: Function to execute for this step
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        """
        self.steps.append(WorkflowStep(name, function, list(args) or None, kwargs or None))

    def execute(self, initial_context: dict[str, Any]) -> WorkflowResult:
        """Execute the workflow with the given context.

        Args:
            initial_context: Initial context data for the workflow

        Returns:
            WorkflowResult: Results of the workflow execution

        """
        context = initial_context.copy()
        context.setdefault("created_objects", [])
        context.setdefault("errors", [])

        steps_results = []
        errors = []

        # Execute all steps until failure or completion
        for step in self.steps:
            step_result = self._execute_single_step(step, context, errors)
            steps_results.append(step_result)

            # Stop on any failure since all steps are critical
            if step_result["status"] == "failed":
                break

        # Calculate summary statistics
        success_count = len([r for r in steps_results if r["status"] == "success"])
        error_count = len(errors)
        total_steps = len(steps_results)

        return WorkflowResult(
            success_count=success_count,
            total_steps=total_steps,
            error_count=error_count,
            steps_results=steps_results,
            errors=errors,
        )

    @staticmethod
    def _execute_single_step(
        step: WorkflowStep, context: dict[str, Any], errors: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Execute a single workflow step with error handling.

        Args:
            step: The workflow step to execute
            context: The workflow execution context
            errors: List to append errors to

        Returns:
            dict[str, Any]: Step execution result

        """
        try:
            # Check if this is the new pattern (with args/kwargs) or old pattern (context function)
            if step.args is not None or step.kwargs is not None:
                # New pattern: direct function call with args/kwargs
                args = step.args or []
                kwargs = step.kwargs or {}
                result = step.function(*args, **kwargs)

                # Normalize result to dict format
                if isinstance(result, dict):
                    normalized_result = result
                else:
                    # For objects returned by create_and_save, create a dict
                    normalized_result = {
                        "status": "created",
                        "node_id": str(getattr(result, "id", "unknown")),
                        "name": str(getattr(result, "name", "unknown")),
                        "message": f"Created {type(result).__name__} node",
                    }
            else:
                # Old pattern: function expects context parameter
                result = step.function(context)
                normalized_result = result

            step_result = {
                "step": step.name,
                "result": normalized_result,
                "status": "success",
            }

            context["created_objects"].append({"step": step.name, "result": step_result["result"], "status": "success"})

        except Exception as e:  # noqa: BLE001
            error_info = {
                "step": step.name,
                "error": str(e),
                "status": "failed",
            }
            errors.append(error_info)

            step_result = {
                "step": step.name,
                "result": {"status": "failed", "error": str(e), "message": f"Step '{step.name}' failed: {e}"},
                "status": "failed",
            }

            context["created_objects"].append({"step": step.name, "result": step_result["result"], "status": "failed"})

        return step_result

    def execute_with_status(
        self,
        initial_context: dict[str, Any],
        *,
        show_details: bool = False,
    ) -> WorkflowResult:
        """Execute workflow with Streamlit status display.

        Args:
            initial_context: Initial context data for the workflow
            show_details: Whether to show detailed step information

        Returns:
            WorkflowResult: Results of the workflow execution

        """
        with st.status(f"Executing {self.workflow_name}...", expanded=True) as status:
            result = self.execute(initial_context)

            # Update status based on results
            if result.error_count == 0:
                status.update(
                    label=f"✅ {self.workflow_name} completed successfully! ({result.success_count}/{result.total_steps} steps)",
                    state="complete",
                    expanded=False,
                )
            elif result.success_count > 0:
                status.update(
                    label=f"⚠️ {self.workflow_name} partially completed ({result.success_count} success, {result.error_count} failed)",
                    state="error",
                    expanded=True,
                )
            else:
                status.update(
                    label=f"❌ {self.workflow_name} failed ({result.error_count} errors)", state="error", expanded=True
                )

            # Show detailed results if requested
            if show_details:
                WorkflowEngine._display_workflow_details(result)

        return result

    @staticmethod
    def _display_workflow_details(result: WorkflowResult) -> None:
        """Display detailed workflow results."""
        for step_result in result.steps_results:
            step_name = step_result["step"]
            status = step_result["status"]

            if status == "success":
                st.success(f"✅ {step_name}: Completed")
            elif status == "failed":
                st.error(f"❌ {step_name}: Failed")
            else:
                st.warning(f"⚠️ {step_name}: Unknown status")

            # Show step result message if available
            if step_result.get("result", {}).get("message"):
                st.caption(step_result["result"]["message"])
