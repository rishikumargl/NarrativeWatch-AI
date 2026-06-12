"""Unit tests for BaseAgent class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.base_agent import BaseAgent, AgentConfig, AgentResult


class TestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def _define_tools(self):
        """Define tools for test agent."""
        return []

    def _get_system_prompt(self) -> str:
        """Get system prompt for test agent."""
        return "You are a test agent."


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_agent_config_creation(self):
        """Test creating an AgentConfig."""
        config = AgentConfig(
            name="test_agent",
            description="A test agent",
            max_iterations=5,
            verbose=False,
            temperature=0.7,
        )
        assert config.name == "test_agent"
        assert config.description == "A test agent"
        assert config.max_iterations == 5
        assert config.verbose is False
        assert config.temperature == 0.7

    def test_agent_config_defaults(self):
        """Test AgentConfig with default values."""
        config = AgentConfig(
            name="test_agent",
            description="A test agent",
        )
        assert config.max_iterations == 5
        assert config.verbose is False
        assert config.temperature == 0.7
        assert config.tools == []

    def test_agent_config_temperature_validation(self):
        """Test temperature validation in AgentConfig."""
        with pytest.raises(ValueError):
            AgentConfig(
                name="test_agent",
                description="A test agent",
                temperature=2.5,  # > 2.0
            )

        with pytest.raises(ValueError):
            AgentConfig(
                name="test_agent",
                description="A test agent",
                temperature=-0.5,  # < 0.0
            )


class TestAgentResult:
    """Tests for AgentResult."""

    def test_agent_result_success(self):
        """Test creating a successful AgentResult."""
        result = AgentResult(
            agent_name="test_agent",
            status="success",
            output={"data": "test"},
            iterations=3,
        )
        assert result.agent_name == "test_agent"
        assert result.status == "success"
        assert result.output == {"data": "test"}
        assert result.iterations == 3
        assert result.error is None

    def test_agent_result_error(self):
        """Test creating an error AgentResult."""
        result = AgentResult(
            agent_name="test_agent",
            status="error",
            output=None,
            error="Test error message",
        )
        assert result.agent_name == "test_agent"
        assert result.status == "error"
        assert result.output is None
        assert result.error == "Test error message"


class TestBaseAgent:
    """Tests for BaseAgent class."""

    @pytest.fixture
    def agent_config(self):
        """Fixture for agent configuration."""
        return AgentConfig(
            name="test_agent",
            description="A test agent for testing",
            max_iterations=5,
            verbose=False,
            temperature=0.7,
        )

    @patch("src.agents.base_agent.ChatVertexAI")
    def test_agent_initialization(self, mock_llm, agent_config):
        """Test agent initialization."""
        mock_llm.return_value = MagicMock()
        agent = TestAgent(agent_config)

        assert agent.config == agent_config
        assert agent.config.name == "test_agent"
        assert agent.logger is not None
        assert agent.executor is None

    def test_agent_validate_input_valid(self, agent_config):
        """Test input validation with valid input."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            agent = TestAgent(agent_config)
            assert agent.validate_input("valid input") is True

    def test_agent_validate_input_empty_string(self, agent_config):
        """Test input validation with empty string."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            agent = TestAgent(agent_config)
            assert agent.validate_input("") is False

    def test_agent_validate_input_invalid_type(self, agent_config):
        """Test input validation with invalid type."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            agent = TestAgent(agent_config)
            assert agent.validate_input(123) is False
            assert agent.validate_input(None) is False
            assert agent.validate_input([]) is False

    def test_agent_repr(self, agent_config):
        """Test agent string representation."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            agent = TestAgent(agent_config)
            repr_str = repr(agent)
            assert "TestAgent" in repr_str
            assert "test_agent" in repr_str

    @patch("src.agents.base_agent.ChatVertexAI")
    def test_agent_run_success(self, mock_llm, agent_config):
        """Test successful agent run."""
        mock_executor = MagicMock()
        mock_executor.invoke.return_value = {"output": "test result", "iterations": 2}

        with patch.object(TestAgent, "_create_executor", return_value=mock_executor):
            agent = TestAgent(agent_config)
            result = agent.run("test input")

            assert result.agent_name == "test_agent"
            assert result.status == "success"
            assert result.output == {"output": "test result", "iterations": 2}
            assert result.error is None

    @patch("src.agents.base_agent.ChatVertexAI")
    def test_agent_run_error(self, mock_llm, agent_config):
        """Test agent run with error."""
        mock_executor = MagicMock()
        mock_executor.invoke.side_effect = Exception("Test error")

        with patch.object(TestAgent, "_create_executor", return_value=mock_executor):
            agent = TestAgent(agent_config)
            result = agent.run("test input")

            assert result.agent_name == "test_agent"
            assert result.status == "error"
            assert result.output is None
            assert "Test error" in result.error

    @patch("src.agents.base_agent.ChatVertexAI")
    def test_agent_run_timeout(self, mock_llm, agent_config):
        """Test agent run with timeout."""
        mock_executor = MagicMock()
        mock_executor.invoke.side_effect = TimeoutError("Timeout")

        with patch.object(TestAgent, "_create_executor", return_value=mock_executor):
            agent = TestAgent(agent_config)
            result = agent.run("test input")

            assert result.agent_name == "test_agent"
            assert result.status == "timeout"
            assert result.output is None
            assert "Timeout" in result.error

    def test_agent_define_tools_override(self, agent_config):
        """Test that _define_tools is properly overridden."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            agent = TestAgent(agent_config)
            tools = agent._define_tools()
            assert isinstance(tools, list)

    def test_agent_get_system_prompt_override(self, agent_config):
        """Test that _get_system_prompt is properly overridden."""
        with patch("src.agents.base_agent.ChatVertexAI"):
            agent = TestAgent(agent_config)
            prompt = agent._get_system_prompt()
            assert isinstance(prompt, str)
            assert "test agent" in prompt
