"""Base agent class for all specialized agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_vertexai import ChatVertexAI
from src.logger import setup_logger
from src.config import settings


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    description: str
    tools: Optional[list[Tool]] = Field(default_factory=list)
    max_iterations: int = Field(default=5)
    verbose: bool = Field(default=False)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AgentResult(BaseModel):
    """Result from agent execution."""
    agent_name: str
    status: str = "success"  # success, error, timeout
    output: Any
    error: Optional[str] = None
    iterations: int = 0


class BaseAgent(ABC):
    """
    Base agent class for all specialized agents in the system.

    All agents inherit from this class and must implement:
    - _define_tools(): Define tools available to the agent
    - _get_system_prompt(): Define the system prompt
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize agent with configuration.

        Args:
            config: AgentConfig instance with agent settings
        """
        self.config = config
        self.logger = setup_logger(f"agents.{config.name}")
        self.llm = self._initialize_llm()
        self.executor = None

        self.logger.info(f"Initializing agent: {config.name}")

    def _initialize_llm(self) -> ChatVertexAI:
        """Initialize the LLM client."""
        if not settings.VERTEX_AI_PROJECT_ID:
            raise ValueError("VERTEX_AI_PROJECT_ID not configured")

        return ChatVertexAI(
            project=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION,
            model_name=settings.VERTEX_AI_MODEL,
            temperature=self.config.temperature,
            verbose=self.config.verbose,
        )

    @abstractmethod
    def _define_tools(self) -> list[Tool]:
        """
        Define tools available to this agent.

        Returns:
            List of Tool objects
        """
        return []

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for this agent.

        Returns:
            System prompt string
        """
        return f"You are {self.config.name}. {self.config.description}"

    def _create_executor(self) -> AgentExecutor:
        """Create and return the agent executor."""
        tools = self._define_tools()
        system_prompt = self._get_system_prompt()

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, tools, prompt)
        executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=self.config.verbose,
            max_iterations=self.config.max_iterations,
            handle_parsing_errors=True,
        )
        return executor

    def run(self, input_data: str) -> AgentResult:
        """
        Run the agent with given input.

        Args:
            input_data: Input string for the agent

        Returns:
            AgentResult with output, status, and metadata
        """
        try:
            if not self.executor:
                self.executor = self._create_executor()

            self.logger.info(f"Running agent: {self.config.name}")
            self.logger.debug(f"Input: {input_data}")

            result = self.executor.invoke({"input": input_data})

            self.logger.info(f"Agent {self.config.name} completed successfully")

            return AgentResult(
                agent_name=self.config.name,
                status="success",
                output=result,
                iterations=result.get("iterations", 0) if isinstance(result, dict) else 0,
            )

        except TimeoutError as e:
            self.logger.error(f"Agent {self.config.name} timed out: {e}")
            return AgentResult(
                agent_name=self.config.name,
                status="timeout",
                output=None,
                error=str(e),
            )

        except Exception as e:
            self.logger.error(f"Agent {self.config.name} error: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.config.name,
                status="error",
                output=None,
                error=str(e),
            )

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input for this agent. Override in subclasses for custom validation.

        Args:
            input_data: Input to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(input_data, str):
            self.logger.warning(f"Invalid input type: {type(input_data)}")
            return False
        if not input_data.strip():
            self.logger.warning("Empty input")
            return False
        return True

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"<{self.__class__.__name__}(name={self.config.name})>"
