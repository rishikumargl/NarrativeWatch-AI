"""Main orchestration engine for workflow execution."""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from src.workflow.state_manager import state_manager, WorkflowState
from src.logger import setup_logger


class OrchestrationEngine:
    """
    Main orchestration engine that executes the workflow.

    Manages agent execution, state transitions, and error handling.
    """

    def __init__(self):
        """Initialize orchestration engine."""
        self.logger = setup_logger("workflow.orchestration")
        self.state_manager = state_manager

    async def execute_workflow(
        self,
        workflow_id: str,
        user_query: str,
        agents: Dict[str, Any],
    ) -> WorkflowState:
        """
        Execute complete workflow with all agents.

        Args:
            workflow_id: Unique workflow identifier
            user_query: User's input query
            agents: Dictionary of agent implementations

        Returns:
            Final WorkflowState with results
        """
        self.logger.info(f"Starting workflow: {workflow_id}")

        # Create workflow state
        state = self.state_manager.create_workflow_state(workflow_id, user_query)
        state.mark_started()

        try:
            # Execute content analyzer
            state = await self._execute_agent(
                state, "content_analyzer", user_query, agents
            )
            if state.any_agent_failed():
                self.logger.warning("Content analyzer failed, continuing with others")

            # Execute RAG agent (parallel)
            state = await self._execute_agent(
                state, "rag_agent", user_query, agents
            )

            # Execute research agent (parallel)
            state = await self._execute_agent(
                state, "research_agent", user_query, agents
            )

            # Execute bias detector
            content_result = self.state_manager.get_workflow_state(workflow_id)
            content_data = content_result.get_agent_state("content_analyzer")
            state = await self._execute_agent(
                state, "bias_detector", content_data.output_data or user_query, agents
            )

            # Execute bot detector
            state = await self._execute_agent(
                state, "bot_detector", user_query, agents
            )

            # Execute campaign detector
            state = await self._execute_agent(
                state, "campaign_detector", user_query, agents
            )

            # Aggregate results
            agent_results = self._aggregate_results(state)

            # Execute synthesis agent
            state = await self._execute_agent(
                state, "synthesis_agent", agent_results, agents
            )

            synthesis_output = state.get_agent_state("synthesis_agent").output_data

            # Execute reviewer agent with reflection loop
            state = await self._execute_reflection_loop(
                state, synthesis_output, agents
            )

            # Mark workflow as completed
            final_result = state.get_agent_state("synthesis_agent").output_data
            self.state_manager.complete_workflow(workflow_id, final_result)

            self.logger.info(f"Workflow completed: {workflow_id}")
            return state

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}", exc_info=True)
            self.state_manager.fail_workflow(workflow_id, str(e))
            raise

    async def _execute_agent(
        self,
        state: WorkflowState,
        agent_name: str,
        input_data: Any,
        agents: Dict[str, Any],
    ) -> WorkflowState:
        """
        Execute a single agent and update state.

        Args:
            state: Current workflow state
            agent_name: Name of agent to execute
            input_data: Input data for agent
            agents: Dictionary of agent implementations

        Returns:
            Updated workflow state
        """
        self.logger.info(f"Executing agent: {agent_name}")

        try:
            # Update state to running
            self.state_manager.update_agent_state(
                state.workflow_id, agent_name, "running"
            )

            # Get agent from dictionary
            if agent_name not in agents:
                raise ValueError(f"Agent not found: {agent_name}")

            agent = agents[agent_name]

            # Execute agent with timeout
            try:
                result = await asyncio.wait_for(
                    self._call_agent(agent, input_data),
                    timeout=120,  # 2 minute timeout
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"Agent {agent_name} timed out")

            # Update state with result
            self.state_manager.update_agent_state(
                state.workflow_id, agent_name, "completed", output=result
            )

            self.logger.info(f"Agent completed: {agent_name}")
            return self.state_manager.get_workflow_state(state.workflow_id)

        except Exception as e:
            self.logger.error(f"Agent failed: {agent_name} - {e}")
            self.state_manager.update_agent_state(
                state.workflow_id, agent_name, "failed", error=str(e)
            )
            return self.state_manager.get_workflow_state(state.workflow_id)

    async def _call_agent(self, agent: Any, input_data: Any) -> Any:
        """Call agent asynchronously."""
        # Convert sync agent call to async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: agent.run(input_data))

    async def _execute_reflection_loop(
        self,
        state: WorkflowState,
        synthesis_result: Any,
        agents: Dict[str, Any],
    ) -> WorkflowState:
        """
        Execute reflection loop with reviewer agent.

        Args:
            state: Current workflow state
            synthesis_result: Result from synthesis agent
            agents: Dictionary of agent implementations

        Returns:
            Updated workflow state with reviewer feedback
        """
        self.logger.info("Starting reflection loop")

        while self.state_manager.start_reflection_attempt(state.workflow_id):
            attempt = state.reflection_attempt

            self.logger.info(f"Reflection attempt {attempt}/{state.reflection_max_attempts}")

            try:
                # Execute reviewer agent
                reviewer = agents.get("reviewer_agent")
                if not reviewer:
                    self.logger.warning("Reviewer agent not available")
                    break

                feedback = await self._call_agent(reviewer, synthesis_result)

                # Check if approved
                if isinstance(feedback, dict) and feedback.get("status") == "APPROVED":
                    self.logger.info("Synthesis approved by reviewer")
                    break

                # If rejected, regenerate
                if isinstance(feedback, dict) and feedback.get("status") == "REJECTED":
                    self.logger.info(f"Regenerating synthesis (attempt {attempt})")

                    # Add feedback to state
                    feedback_text = feedback.get("feedback", "No specific feedback")
                    state.add_reflection_feedback(feedback_text)

                    # Regenerate with feedback
                    synthesis_agent = agents.get("synthesis_agent")
                    if synthesis_agent:
                        synthesis_result = await self._call_agent(
                            synthesis_agent,
                            {
                                "previous_result": synthesis_result,
                                "feedback": feedback_text,
                            },
                        )

                        # Update synthesis agent state
                        self.state_manager.update_agent_state(
                            state.workflow_id,
                            "synthesis_agent",
                            "completed",
                            output=synthesis_result,
                        )

            except Exception as e:
                self.logger.error(f"Reflection loop error: {e}")
                state.add_reflection_feedback(f"Error: {str(e)}")

        self.logger.info(
            f"Reflection loop completed (attempts: {state.reflection_attempt})"
        )
        return self.state_manager.get_workflow_state(state.workflow_id)

    def _aggregate_results(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Aggregate results from all completed agents.

        Args:
            state: Current workflow state

        Returns:
            Dictionary of aggregated results
        """
        results = {}
        for agent_name, agent_state in state.agent_states.items():
            if agent_state.status == "completed":
                results[agent_name] = {
                    "output": agent_state.output_data,
                    "duration": agent_state.duration_seconds,
                    "retry_count": agent_state.retry_count,
                }
            elif agent_state.status == "failed":
                results[agent_name] = {
                    "error": agent_state.error,
                    "duration": agent_state.duration_seconds,
                }

        self.logger.debug(f"Aggregated results from {len(results)} agents")
        return results

    def get_workflow_summary(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get summary of workflow execution.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow summary dictionary
        """
        return self.state_manager.get_workflow_summary(workflow_id)


# Global orchestration engine instance
orchestration_engine = OrchestrationEngine()
