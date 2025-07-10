"""Tests for the workflow engine module."""

from typing import Any

from src.workflow_engine import WorkflowEngine, WorkflowStep


class TestWorkflowEngine:
    """Test cases for the WorkflowEngine class."""

    def test_workflow_engine_creation(self):
        """Test basic workflow engine creation."""
        workflow = WorkflowEngine("Test Workflow")
        assert workflow.workflow_name == "Test Workflow"
        assert len(workflow.steps) == 0

    def test_add_step(self):
        """Test adding steps to workflow."""
        workflow = WorkflowEngine("Test Workflow")

        def dummy_step(_context: dict[str, Any]) -> dict[str, str]:
            return {"status": "success", "message": "Step completed"}

        workflow.add_step(
            "Test Step",
            dummy_step,
        )

        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "Test Step"

    def test_workflow_execution_success(self):
        """Test successful workflow execution."""
        workflow = WorkflowEngine("Test Workflow")

        def step1(context: dict[str, Any]) -> dict[str, str]:
            context["step1_done"] = True
            return {"status": "success", "message": "Step 1 completed"}

        def step2(context: dict[str, Any]) -> dict[str, str]:
            assert context["step1_done"] is True
            return {"status": "success", "message": "Step 2 completed"}

        workflow.add_step("Step 1", step1)
        workflow.add_step("Step 2", step2)

        result = workflow.execute({"initial": "data"})

        assert result.success_count == 2
        assert result.total_steps == 2
        assert result.error_count == 0

    def test_workflow_execution_with_error(self):
        """Test workflow execution with step error."""
        workflow = WorkflowEngine("Test Workflow")

        def step1(_context: dict[str, Any]) -> dict[str, str]:
            return {"status": "success", "message": "Step 1 completed"}

        def step2(_context: dict[str, Any]) -> dict[str, str]:
            error_msg = "Step 2 failed"
            raise ValueError(error_msg)

        workflow.add_step("Step 1", step1)
        workflow.add_step("Step 2", step2)

        result = workflow.execute({"initial": "data"})

        assert result.success_count == 1
        assert result.total_steps == 2  # Both steps attempted, second one failed
        assert result.error_count == 1

    def test_workflow_step_namedtuple(self):
        """Test WorkflowStep NamedTuple creation."""

        def dummy_function() -> dict[str, str]:
            return {"status": "success"}

        step = WorkflowStep(
            name="Test Step",
            function=dummy_function,
        )

        assert step.name == "Test Step"
        assert step.function == dummy_function
