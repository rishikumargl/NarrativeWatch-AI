"""Vertex AI / Gemini LLM client wrapper."""

import os
import logging
from typing import Optional, List, Iterator
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for Vertex AI Gemini LLM."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "gemini-2.5-pro",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """Initialize Vertex AI LLM client.

        Args:
            project_id: Google Cloud project ID. If None, reads from env.
            location: GCP region. Defaults to us-central1.
            model_name: Gemini model name.
            temperature: Model temperature (0-1).
            max_tokens: Max output tokens.
        """
        self.project_id = project_id or os.getenv("VERTEX_AI_PROJECT_ID")
        self.location = location or os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.project_id:
            raise ValueError("VERTEX_AI_PROJECT_ID environment variable not set")

        # Initialize Vertex AI
        try:
            vertexai.init(project=self.project_id, location=self.location)
            logger.info(f"✓ Vertex AI initialized: {self.project_id}/{self.location}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise

        # Initialize model
        self.model = GenerativeModel(self.model_name)
        logger.info(f"✓ LLM client initialized: {self.model_name}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using Gemini.

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated text
        """
        try:
            # Combine prompts
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            # Generate
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature or self.temperature,
                    "max_output_tokens": max_tokens or self.max_tokens,
                    "top_p": 0.95,
                    "top_k": 40,
                },
            )

            text = response.text
            logger.info(f"✓ Generated {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise

    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Stream text generation using Gemini.

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Yields:
            Generated text chunks
        """
        try:
            # Combine prompts
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            # Stream
            response = self.model.generate_content(
                full_prompt,
                stream=True,
                generation_config={
                    "temperature": temperature or self.temperature,
                    "max_output_tokens": max_tokens or self.max_tokens,
                    "top_p": 0.95,
                    "top_k": 40,
                },
            )

            logger.info("✓ Streaming generation started")
            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise

    def classify(
        self,
        text: str,
        labels: List[str],
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Classify text into categories.

        Args:
            text: Text to classify
            labels: Possible labels/categories
            system_prompt: Optional system instruction

        Returns:
            Classification result
        """
        prompt = f"""Classify the following text into one of these categories: {', '.join(labels)}

Text: {text}

Respond with ONLY the category name, nothing else."""

        classification = self.generate(prompt, system_prompt=system_prompt)

        return {
            "text": text,
            "labels": labels,
            "classification": classification.strip(),
        }

    def extract_entities(
        self,
        text: str,
        entity_types: List[str],
    ) -> dict:
        """Extract entities from text.

        Args:
            text: Text to analyze
            entity_types: Types of entities to extract

        Returns:
            Extracted entities
        """
        prompt = f"""Extract the following entity types from the text: {', '.join(entity_types)}

Text: {text}

Return as JSON with entity types as keys and lists of entities as values."""

        result = self.generate(prompt)

        return {
            "text": text,
            "entity_types": entity_types,
            "entities": result,
        }

    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
    ) -> str:
        """Summarize text.

        Args:
            text: Text to summarize
            max_length: Max length of summary (in words)

        Returns:
            Summary text
        """
        length_constraint = f" in {max_length} words" if max_length else ""
        prompt = f"Summarize the following text{length_constraint}:\n\n{text}"

        return self.generate(prompt)

    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis result
        """
        prompt = f"""Analyze the sentiment of the following text. Respond with a JSON object with:
- sentiment: positive, negative, or neutral
- score: confidence score (0-1)
- explanation: brief explanation

Text: {text}"""

        result = self.generate(prompt)

        return {
            "text": text,
            "analysis": result,
        }

    def check_health(self) -> bool:
        """Check if LLM is accessible.

        Returns:
            True if LLM is working
        """
        try:
            response = self.generate("Say 'OK'")
            is_healthy = response and len(response) > 0
            logger.info(f"{'✓' if is_healthy else '✗'} LLM health check: {is_healthy}")
            return is_healthy
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False
