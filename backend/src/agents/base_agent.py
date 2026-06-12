"""Base agent class for all NarrativeWatch AI agents using Groq LLM."""

from typing import List, Dict, Any, Optional
import logging
import os
from src.config import settings

try:
    from langchain_groq import ChatGroq
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class AgentConfig:
    """Configuration for agents."""

    def __init__(
        self,
        name: str,
        description: str,
        temperature: float = 0.7,
        max_iterations: int = 5,
        model_name: str = "mixtral-8x7b-32768",
        timeout: int = 300
    ):
        """Initialize agent configuration."""
        self.name = name
        self.description = description
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.model_name = model_name
        self.timeout = timeout


class BaseAgent:
    """Base class for all agents in the NarrativeWatch system using Groq."""

    def __init__(
        self,
        config: Optional['AgentConfig'] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_iterations: int = 5,
        groq_api_key: Optional[str] = None,
        model_name: str = "mixtral-8x7b-32768"
    ):
        """Initialize agent with Groq LLM."""
        if config:
            self.name = config.name
            self.description = config.description
            self.model_name = config.model_name
            self.temperature = config.temperature
            self.max_iterations = config.max_iterations
        else:
            self.name = name
            self.description = description
            self.model_name = model_name
            self.temperature = temperature
            self.max_iterations = max_iterations

        self.tools = tools or []
        self.groq_api_key = groq_api_key or settings.GROQ_API_KEY

        self.llm = self._initialize_llm()
        logger.info(f"Initialized {self.name} agent with model {self.model_name}")

    def _initialize_llm(self):
        """Initialize Groq language model."""
        if not LANGCHAIN_AVAILABLE:
            logger.warning(f"{self.name}: LangChain not available")
            return None

        try:
            return ChatGroq(
                model_name=self.model_name,
                temperature=self.temperature,
                groq_api_key=self.groq_api_key,
                max_tokens=2048
            )
        except Exception as e:
            logger.error(f"{self.name}: Failed to initialize LLM: {e}")
            return None

    def run(self, input_data: str) -> Dict[str, Any]:
        """Execute the agent."""
        try:
            if not self.llm:
                return {
                    "status": "error",
                    "message": "LLM not initialized",
                    "agent": self.name
                }

            logger.info(f"{self.name} processing input: {input_data[:100]}...")

            messages = [
                {
                    "role": "system",
                    "content": f"You are {self.name}. {self.description}\n\nYour goals:\n1. Provide accurate, evidence-based analysis\n2. Consider multiple perspectives\n3. Cite sources when making claims\n4. Be transparent about uncertainty\n5. Structure responses clearly"
                },
                {
                    "role": "user",
                    "content": input_data
                }
            ]

            response = self.llm.invoke(messages)
            return {
                "status": "success",
                "data": response.content if hasattr(response, 'content') else str(response),
                "agent": self.name
            }
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name
            }

    def stream(self, input_data: str):
        """Stream response from the agent."""
        try:
            if not self.llm:
                yield {"error": "LLM not initialized"}
                return

            messages = [
                {
                    "role": "system",
                    "content": f"You are {self.name}. {self.description}"
                },
                {
                    "role": "user",
                    "content": input_data
                }
            ]

            for chunk in self.llm.stream(messages):
                if hasattr(chunk, 'content'):
                    yield {"content": chunk.content}
                else:
                    yield {"content": str(chunk)}
        except Exception as e:
            logger.error(f"Stream error in {self.name}: {str(e)}")
            yield {"error": str(e)}

    def add_tool(self, tool: Dict) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)
        logger.info(f"Added tool to {self.name}: {tool.get('name', 'unknown')}")
