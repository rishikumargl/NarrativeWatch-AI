"""State management for workflow orchestration."""

from typing import Any, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from src.logger import setup_logger


class ExecutionState(BaseModel):
    """State for a single agent execution."""
    agent_name: str
    status: str = "pending"  # pending, running, completed, failed
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    retry_count: int = 0

    def mark_running(self):
        """Mark state as running."""
        self.status = "running"
        self.start_time = datetime.utcnow()

    def mark_completed(self, output: Any):
        """Mark state as completed with output."""
        self.status = "completed"
        self.output_data = output
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()

    def mark_failed(self, error: str):
        """Mark state as failed with error."""
        self.status = "failed"
        self.error = error
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()

    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.duration_seconds = 0.0


class WorkflowState(BaseModel):
    """State for entire workflow execution."""
    workflow_id: str
    user_query: str
    status: str = "initialized"  # initialized, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0

    # Agent states
    agent_states: Dict[str, ExecutionState] = Field(default_factory=dict)

    # Reflection loop tracking
    reflection_attempt: int = 1
    reflection_max_attempts: int = 3
    reflection_feedback: list[str] = Field(default_factory=list)

    # Final results
    final_result: Optional[Any] = None
    error_message: Optional[str] = None

    def mark_started(self):
        """Mark workflow as started."""
        self.status = "running"
        self.start_time = datetime.utcnow()

    def mark_completed(self, result: Any):
        """Mark workflow as completed."""
        self.status = "completed"
        self.final_result = result
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()

    def mark_failed(self, error: str):
        """Mark workflow as failed."""
        self.status = "failed"
        self.error_message = error
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()

    def add_agent_state(self, agent_name: str) -> ExecutionState:
        """Add or get agent state."""
        if agent_name not in self.agent_states:
            self.agent_states[agent_name] = ExecutionState(agent_name=agent_name)
        return self.agent_states[agent_name]

    def get_agent_state(self, agent_name: str) -> Optional[ExecutionState]:
        """Get agent state."""
        return self.agent_states.get(agent_name)

    def all_agents_completed(self) -> bool:
        """Check if all agents have completed."""
        if not self.agent_states:
            return False
        return all(state.status == "completed" for state in self.agent_states.values())

    def any_agent_failed(self) -> bool:
        """Check if any agent has failed."""
        return any(state.status == "failed" for state in self.agent_states.values())

    def add_reflection_feedback(self, feedback: str):
        """Add feedback from reflection loop."""
        self.reflection_feedback.append(feedback)
        self.reflection_attempt += 1


class StateManager:
    """Manages workflow state across execution."""

    def __init__(self):
        """Initialize state manager."""
        self.logger = setup_logger("workflow.state_manager")
        self.states: Dict[str, WorkflowState] = {}

    def create_workflow_state(
        self,
        workflow_id: str,
        user_query: str,
        max_reflection_attempts: int = 3,
    ) -> WorkflowState:
        """
        Create a new workflow state.

        Args:
            workflow_id: Unique workflow identifier
            user_query: User's input query
            max_reflection_attempts: Max reflection loop attempts

        Returns:
            WorkflowState instance
        """
        state = WorkflowState(
            workflow_id=workflow_id,
            user_query=user_query,
            reflection_max_attempts=max_reflection_attempts,
        )
        self.states[workflow_id] = state
        self.logger.info(f"Created workflow state: {workflow_id}")
        return state

    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state by ID."""
        return self.states.get(workflow_id)

    def update_agent_state(
        self,
        workflow_id: str,
        agent_name: str,
        status: str,
        output: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> Optional[ExecutionState]:
        """
        Update agent execution state.

        Args:
            workflow_id: Workflow identifier
            agent_name: Name of the agent
            status: New status (running, completed, failed)
            output: Output data if completed
            error: Error message if failed

        Returns:
            Updated ExecutionState
        """
        workflow = self.get_workflow_state(workflow_id)
        if not workflow:
            self.logger.error(f"Workflow not found: {workflow_id}")
            return None

        agent_state = workflow.add_agent_state(agent_name)

        if status == "running":
            agent_state.mark_running()
        elif status == "completed":
            agent_state.mark_completed(output)
            self.logger.info(
                f"Agent {agent_name} completed in {agent_state.duration_seconds:.2f}s"
            )
        elif status == "failed":
            agent_state.mark_failed(error or "Unknown error")
            self.logger.error(f"Agent {agent_name} failed: {error}")

        return agent_state

    def start_reflection_attempt(self, workflow_id: str) -> bool:
        """
        Start a new reflection attempt.

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if attempt is within limit, False otherwise
        """
        workflow = self.get_workflow_state(workflow_id)
        if not workflow:
            return False

        if workflow.reflection_attempt >= workflow.reflection_max_attempts:
            self.logger.warning(
                f"Max reflection attempts ({workflow.reflection_max_attempts}) reached"
            )
            return False

        self.logger.info(
            f"Starting reflection attempt {workflow.reflection_attempt} "
            f"(max: {workflow.reflection_max_attempts})"
        )
        return True

    def complete_workflow(
        self,
        workflow_id: str,
        result: Any,
    ) -> Optional[WorkflowState]:
        """
        Mark workflow as completed.

        Args:
            workflow_id: Workflow identifier
            result: Final result

        Returns:
            Updated WorkflowState
        """
        workflow = self.get_workflow_state(workflow_id)
        if not workflow:
            self.logger.error(f"Workflow not found: {workflow_id}")
            return None

        workflow.mark_completed(result)
        self.logger.info(
            f"Workflow {workflow_id} completed in {workflow.duration_seconds:.2f}s"
        )
        return workflow

    def fail_workflow(
        self,
        workflow_id: str,
        error: str,
    ) -> Optional[WorkflowState]:
        """
        Mark workflow as failed.

        Args:
            workflow_id: Workflow identifier
            error: Error message

        Returns:
            Updated WorkflowState
        """
        workflow = self.get_workflow_state(workflow_id)
        if not workflow:
            self.logger.error(f"Workflow not found: {workflow_id}")
            return None

        workflow.mark_failed(error)
        self.logger.error(f"Workflow {workflow_id} failed: {error}")
        return workflow

    def get_workflow_summary(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of workflow execution.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Dictionary with workflow summary
        """
        workflow = self.get_workflow_state(workflow_id)
        if not workflow:
            return None

        agent_summaries = {}
        for agent_name, agent_state in workflow.agent_states.items():
            agent_summaries[agent_name] = {
                "status": agent_state.status,
                "duration_seconds": agent_state.duration_seconds,
                "retry_count": agent_state.retry_count,
                "has_output": agent_state.output_data is not None,
                "has_error": agent_state.error is not None,
            }

        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "user_query": workflow.user_query,
            "duration_seconds": workflow.duration_seconds,
            "reflection_attempts": workflow.reflection_attempt,
            "agent_summaries": agent_summaries,
            "error_message": workflow.error_message,
        }

    def clear_state(self, workflow_id: str):
        """Clear state for a workflow."""
        if workflow_id in self.states:
            del self.states[workflow_id]
            self.logger.info(f"Cleared state for workflow: {workflow_id}")

    def clear_all_states(self):
        """Clear all stored states."""
        self.states.clear()
        self.logger.info("Cleared all workflow states")


# Global state manager instance
state_manager = StateManager()
