"""Base agent class for all NarrativeWatch AI agents."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

try:
    from langchain_core.tools import Tool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_google_vertexai import ChatVertexAI
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    # Mock imports for testing
    Tool = None
    ChatPromptTemplate = None
    MessagesPlaceholder = None
    ChatVertexAI = None
    AgentExecutor = None
    create_tool_calling_agent = None

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the NarrativeWatch system."""

    def __init__(self, name: str, description: str, model_name: str = "gemini-2.5-pro"):
        """
        Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            model_name: LLM model to use
        """
        self.name = name
        self.description = description
        self.model_name = model_name
        self.llm = self._initialize_llm()
        self.tools = self._define_tools()
        self.executor = self._create_executor()
        logger.info(f"Initialized {self.name} agent")

    def _initialize_llm(self):
        """Initialize the language model."""
        if ChatVertexAI:
            return ChatVertexAI(model_name=self.model_name, temperature=0.7)
        else:
            logger.warning("Vertex AI not available, using mock LLM")
            return None

    def _define_tools(self) -> List:
        """
        Define tools for this agent. Override in subclasses.

        Returns:
            List of Tool objects
        """
        return []

    def _create_executor(self):
        """Create agent executor with tools."""
        if not ChatPromptTemplate:
            logger.warning("LangChain not available, executor will be None")
            return None

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are {self.name}. {self.description}"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        return executor

    @abstractmethod
    def run(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute agent. Must be implemented by subclasses.

        Args:
            input_data: Input data for the agent

        Returns:
            Dict with agent results
        """
        pass

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data. Override in subclasses for custom validation."""
        return input_data is not None

    def format_output(self, result: Any) -> Dict[str, Any]:
        """Format agent output. Override in subclasses for custom formatting."""
        return {"status": "success", "result": result}

    def invoke(self, input_data: str) -> Dict[str, Any]:
        """
        Invoke agent with error handling.

        Args:
            input_data: Input for the agent

        Returns:
            Agent output
        """
        try:
            if not self.validate_input(input_data):
                return {"status": "error", "message": "Invalid input"}

            result = self.executor.invoke({"input": str(input_data)})
            return self.format_output(result)
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
