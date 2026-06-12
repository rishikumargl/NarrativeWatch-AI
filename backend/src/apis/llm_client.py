"""Groq LLM client wrapper."""

import os
import logging
from typing import Optional, List, Iterator
from groq import Groq

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for Groq LLM."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "mixtral-8x7b-32768",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """Initialize Groq LLM client.

        Args:
            api_key: Groq API key. If None, reads from GROQ_API_KEY env.
            model_name: Groq model name (default: mixtral-8x7b-32768).
            temperature: Model temperature (0-1).
            max_tokens: Max output tokens.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"[OK] Groq LLM client initialized: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            raise

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using Groq.

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated text
        """
        try:
            messages = []

            # Add system message if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add user message
            messages.append({"role": "user", "content": prompt})

            # Generate
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                top_p=0.95,
            )

            text = response.choices[0].message.content
            logger.info(f"[OK] Generated {len(text)} characters")
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
        """Stream text generation using Groq.

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Yields:
            Generated text chunks
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            # Stream
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                top_p=0.95,
                stream=True,
            )

            logger.info("[OK] Streaming generation started")
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

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
            logger.info(f"{'[OK]' if is_healthy else '[FAIL]'} LLM health check: {is_healthy}")
            return is_healthy
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False
