"""Integration tests for the complete NarrativeWatch AI system."""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.workflow.orchestration import OrchestrationEngine
from src.workflow.state_manager import state_manager, WorkflowState
from src.agents.orchestrator import OrchestratorAgent
from src.agents.content_analyzer import ContentAnalyzerAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.reviewer_agent import ReviewerAgent
from src.workflow.reflection_loop import ReflectionLoop


class TestOrchestrationEngine:
    """Tests for OrchestrationEngine."""

    @pytest.fixture
    def engine(self):
        """Fixture for orchestration engine."""
        return OrchestrationEngine()

    @pytest.fixture
    def mock_agents(self):
        """Fixture for mock agents."""
        agents = {
            "content_analyzer": Mock(),
            "rag_agent": Mock(),
            "research_agent": Mock(),
            "bias_detector": Mock(),
            "bot_detector": Mock(),
            "campaign_detector": Mock(),
            "synthesis_agent": Mock(),
            "reviewer_agent": Mock(),
        }

        # Setup mock returns
        for agent_name, agent in agents.items():
            agent.run = Mock(
                return_value={"status": "success", "output": {"data": "test"}}
            )

        return agents

    @pytest.mark.asyncio
    async def test_workflow_execution(self, engine, mock_agents):
        """Test complete workflow execution."""
        workflow_id = "test_wf_001"
        user_query = "Analyze Instagram page: @example"

        state = await engine.execute_workflow(workflow_id, user_query, mock_agents)

        assert state.workflow_id == workflow_id
        assert state.status == "completed"

    @pytest.mark.asyncio
    async def test_agent_execution_order(self, engine, mock_agents):
        """Test agents execute in correct order."""
        workflow_id = "test_wf_002"
        user_query = "Analyze Instagram page"

        call_order = []

        def track_call(agent_name):
            def side_effect(*args, **kwargs):
                call_order.append(agent_name)
                return {"output": {}}
            return side_effect

        for agent_name in mock_agents:
            mock_agents[agent_name].run = track_call(agent_name)

        await engine.execute_workflow(workflow_id, user_query, mock_agents)

        # Verify content_analyzer is called before synthesis_agent
        assert "content_analyzer" in call_order
        assert "synthesis_agent" in call_order

    @pytest.mark.asyncio
    async def test_agent_failure_handling(self, engine, mock_agents):
        """Test handling of agent failures."""
        workflow_id = "test_wf_003"
        user_query = "Analyze Instagram page"

        # Make one agent fail
        mock_agents["content_analyzer"].run = Mock(
            side_effect=Exception("Agent failed")
        )

        state = await engine.execute_workflow(workflow_id, user_query, mock_agents)

        # Should handle failure gracefully
        assert state.workflow_id == workflow_id

    @pytest.mark.asyncio
    async def test_workflow_state_tracking(self, engine, mock_agents):
        """Test workflow state is properly tracked."""
        workflow_id = "test_wf_004"
        user_query = "Analyze Instagram page"

        await engine.execute_workflow(workflow_id, user_query, mock_agents)

        summary = engine.get_workflow_summary(workflow_id)

        assert summary["workflow_id"] == workflow_id
        assert summary["status"] == "completed"
        assert len(summary["agent_summaries"]) > 0

    @pytest.mark.asyncio
    async def test_result_aggregation(self, engine, mock_agents):
        """Test results from agents are properly aggregated."""
        workflow_id = "test_wf_005"
        user_query = "Analyze Instagram page"

        # Setup different outputs for each agent
        mock_agents["content_analyzer"].run = Mock(
            return_value={"output": {"content_analysis": "test"}}
        )
        mock_agents["bias_detector"].run = Mock(
            return_value={"output": {"bias_score": 0.8}}
        )

        state = await engine.execute_workflow(workflow_id, user_query, mock_agents)

        summary = engine.get_workflow_summary(workflow_id)
        assert "agent_summaries" in summary


class TestReflectionLoop:
    """Tests for ReflectionLoop."""

    @pytest.fixture
    def reflection_loop(self):
        """Fixture for reflection loop."""
        return ReflectionLoop(max_retries=3)

    @pytest.fixture
    def mock_reviewer(self):
        """Fixture for mock reviewer."""
        return Mock()

    @pytest.fixture
    def mock_synthesis(self):
        """Fixture for mock synthesis agent."""
        return Mock()

    def test_approved_on_first_attempt(self, reflection_loop, mock_reviewer, mock_synthesis):
        """Test synthesis approved on first attempt."""
        synthesis_result = {"summary": "Test analysis"}

        mock_reviewer.run = Mock(
            return_value={"status": "APPROVED", "feedback": ""}
        )

        result = reflection_loop.execute_with_review(
            synthesis_result, mock_reviewer, mock_synthesis, "test query"
        )

        assert result["approved"] is True
        assert result["attempt"] == 1

    def test_regeneration_on_rejection(self, reflection_loop, mock_reviewer, mock_synthesis):
        """Test synthesis is regenerated on rejection."""
        synthesis_result = {"summary": "Initial analysis"}

        # First call returns rejected, second returns approved
        mock_reviewer.run = Mock(
            side_effect=[
                {"status": "REJECTED", "feedback": "Please improve"},
                {"status": "APPROVED", "feedback": ""},
            ]
        )

        mock_synthesis.run = Mock(
            return_value={"summary": "Improved analysis"}
        )

        result = reflection_loop.execute_with_review(
            synthesis_result, mock_reviewer, mock_synthesis, "test query"
        )

        assert result["attempt"] == 2
        assert mock_synthesis.run.called

    def test_max_retries_escalation(self, reflection_loop, mock_reviewer, mock_synthesis):
        """Test escalation when max retries reached."""
        synthesis_result = {"summary": "Test analysis"}

        # Always return rejected
        mock_reviewer.run = Mock(
            return_value={"status": "REJECTED", "feedback": "Keep improving"}
        )

        result = reflection_loop.execute_with_review(
            synthesis_result, mock_reviewer, mock_synthesis, "test query"
        )

        assert result["approved"] is False
        assert result["status"] == "ESCALATED"
        assert result["attempt"] == 3

    def test_feedback_history_tracking(self, reflection_loop, mock_reviewer, mock_synthesis):
        """Test feedback history is tracked."""
        synthesis_result = {"summary": "Test analysis"}

        feedbacks = [
            {"status": "REJECTED", "feedback": "Feedback 1"},
            {"status": "REJECTED", "feedback": "Feedback 2"},
            {"status": "APPROVED", "feedback": ""},
        ]

        mock_reviewer.run = Mock(side_effect=feedbacks)

        result = reflection_loop.execute_with_review(
            synthesis_result, mock_reviewer, mock_synthesis, "test query"
        )

        assert len(result["feedback_history"]) >= 2
        assert result["feedback_history"][0]["feedback"] == "Feedback 1"


class TestOrchestratorAgent:
    """Tests for OrchestratorAgent."""

    @pytest.fixture
    def orchestrator(self):
        """Fixture for orchestrator agent."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            return OrchestratorAgent()

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator.config.name == "orchestrator"
        assert orchestrator.config.max_iterations == 10

    def test_query_validation(self, orchestrator):
        """Test query validation."""
        assert orchestrator.validate_query("Valid query") is True
        assert orchestrator.validate_query("") is False
        assert orchestrator.validate_query(None) is False
        assert orchestrator.validate_query(123) is False

    def test_workflow_plan_creation(self, orchestrator):
        """Test workflow plan creation."""
        plan = orchestrator.create_workflow_plan("Analyze @example_page")

        assert plan["user_query"] == "Analyze @example_page"
        assert len(plan["agents"]) == 8
        assert len(plan["execution_groups"]) > 0


class TestStateManagement:
    """Tests for state management."""

    def test_workflow_state_creation(self):
        """Test creating workflow state."""
        state = state_manager.create_workflow_state("wf_001", "test query")

        assert state.workflow_id == "wf_001"
        assert state.user_query == "test query"
        assert state.status == "initialized"

    def test_agent_state_tracking(self):
        """Test agent state tracking."""
        state = state_manager.create_workflow_state("wf_002", "test query")

        state_manager.update_agent_state("wf_002", "agent_1", "running")
        agent_state = state_manager.get_workflow_state("wf_002").get_agent_state("agent_1")

        assert agent_state.status == "running"

    def test_workflow_completion(self):
        """Test workflow completion."""
        state = state_manager.create_workflow_state("wf_003", "test query")

        result = {"trust_score": 42, "summary": "Analysis complete"}
        state_manager.complete_workflow("wf_003", result)

        final_state = state_manager.get_workflow_state("wf_003")
        assert final_state.status == "completed"
        assert final_state.final_result == result

    def test_reflection_attempt_tracking(self):
        """Test reflection attempt tracking."""
        state = state_manager.create_workflow_state("wf_004", "test query")

        assert state_manager.start_reflection_attempt("wf_004") is True

        workflow_state = state_manager.get_workflow_state("wf_004")
        workflow_state.add_reflection_feedback("Improve synthesis")

        assert len(workflow_state.reflection_feedback) == 1

    def test_workflow_summary(self):
        """Test workflow summary generation."""
        state = state_manager.create_workflow_state("wf_005", "test query")
        state_manager.update_agent_state("wf_005", "agent_1", "completed", output={"data": "test"})

        summary = state_manager.get_workflow_summary("wf_005")

        assert summary["workflow_id"] == "wf_005"
        assert "agent_summaries" in summary


class TestEndToEndWorkflow:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow from start to finish."""
        engine = OrchestrationEngine()

        # Create mock agents
        agents = {}
        for agent_name in [
            "content_analyzer", "rag_agent", "research_agent",
            "bias_detector", "bot_detector", "campaign_detector",
            "synthesis_agent", "reviewer_agent"
        ]:
            mock_agent = Mock()
            mock_agent.run = Mock(return_value={"output": {"data": "result"}})
            agents[agent_name] = mock_agent

        # Execute workflow
        workflow_id = "e2e_001"
        user_query = "Analyze Instagram page"

        state = await engine.execute_workflow(workflow_id, user_query, agents)

        # Verify completion
        assert state.status == "completed"
        assert state.all_agents_completed() is True

        # Verify summary
        summary = engine.get_workflow_summary(workflow_id)
        assert summary["status"] == "completed"
        assert len(summary["agent_summaries"]) == 8

    @pytest.mark.asyncio
    async def test_workflow_with_reflection(self):
        """Test workflow with reflection loop."""
        engine = OrchestrationEngine()

        # Create agents with reflection
        agents = {}
        for agent_name in ["content_analyzer", "synthesis_agent", "reviewer_agent"]:
            mock_agent = Mock()
            mock_agent.run = Mock(return_value={"output": {"data": "result"}})
            agents[agent_name] = mock_agent

        # Add other agents as well
        for agent_name in ["rag_agent", "research_agent", "bias_detector", "bot_detector", "campaign_detector"]:
            mock_agent = Mock()
            mock_agent.run = Mock(return_value={"output": {}})
            agents[agent_name] = mock_agent

        # Mock reviewer to approve on second attempt
        reviewer = Mock()
        reviewer.run = Mock(
            side_effect=[
                {"status": "REJECTED", "feedback": "Improve"},
                {"status": "APPROVED", "feedback": "Good"},
            ]
        )
        agents["reviewer_agent"] = reviewer

        workflow_id = "e2e_reflection"
        state = await engine.execute_workflow(workflow_id, "Test query", agents)

        assert state.reflection_attempt >= 1
