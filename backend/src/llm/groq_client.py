import os
from openai import OpenAI
from langchain_groq import ChatGroq
from src.config import config
import logging

logger = logging.getLogger(__name__)

class HFInferenceWrapper:
    """Simple wrapper for HuggingFace Inference API"""

    def __init__(self, client, model_name, temperature, max_tokens):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, prompt: str) -> str:
        """Call HuggingFace inference API"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ HF Inference error: {e}")
            raise

class HybridLLMClient:
    """Hybrid client: HF for synthesis, Groq for reviewer"""

    def __init__(self):
        # ===== SYNTHESIS: HuggingFace Inference API =====
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not set in environment")

        openai_client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )

        self.synthesis_llm = HFInferenceWrapper(
            client=openai_client,
            model_name="openai/gpt-oss-120b:groq",
            temperature=0.3,
            max_tokens=2048
        )
        logger.info("✅ Synthesis model: HuggingFace Inference (gpt-oss-120b:groq)")

        # ===== REVIEWER: Groq API =====
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")

        self.reviewer_llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=1024
        )
        logger.info("Reviewer model: Groq API (llama-3.1-8b-instant)")

        # Default LLM
        self.llm = self.synthesis_llm

    def invoke(self, prompt: str, model_type: str = "synthesis") -> str:
        """Send prompt and get response

        Args:
            prompt: The prompt to send
            model_type: "synthesis" (HF) or "reviewer" (Groq)
        """
        try:
            if model_type == "reviewer":
                response = self.reviewer_llm.invoke(prompt)
                return response.content
            else:
                response = self.synthesis_llm.invoke(prompt)
                return response
        except Exception as e:
            logger.error(f"❌ LLM error ({model_type}): {e}")
            raise

    def get_llm(self, model_type: str = "synthesis"):
        """Get LLM instance"""
        if model_type == "reviewer":
            return self.reviewer_llm
        return self.synthesis_llm

    def get_synthesis_llm(self):
        """Get synthesis LLM (HuggingFace)"""
        return self.synthesis_llm

    def get_reviewer_llm(self):
        """Get reviewer LLM (Groq)"""
        return self.reviewer_llm

# Initialize hybrid client
groq_client = HybridLLMClient()
