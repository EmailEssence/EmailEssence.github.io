from typing import Dict, TypeVar, List, Optional
from datetime import datetime, timezone
import json
from google import genai
from google.genai import types
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
# internal
from app.services.summarization.prompts import PromptManager
from app.utils.config import ProviderModel, SummarizerProvider
from app.services.summarization.providers.openai.openai import OpenAIBackend, OpenAIEmailSummarizer
from app.models import SummarySchema
from app.services.summarization.types import ModelBackend, ModelConfig
from app.services.summarization.prompts import PromptVersion
from .prompts import GeminiPromptManager


T = TypeVar('T')



class GeminiBackend(ModelBackend):
    """Native Gemini implementation using Google's API directly."""
    
    def __init__(
        self,
        api_key: str,
        prompt_manager: PromptManager,
        model: str = ProviderModel.default_for_provider(SummarizerProvider.GOOGLE),
        temperature: float = 0.3,
        max_tokens: int = 150
    ):
        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
        # Get the async client
        self.async_client = self.client.aio
        self.prompt_manager = prompt_manager
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @retry(
        retry=retry_if_exception_type((
            Exception  # Replace with specific Gemini exceptions when known
        )),
        stop=stop_after_attempt(2)
    )
    async def generate_summary(
        self,
        content: str,
        config: Optional[ModelConfig] = None
    ) -> tuple[str, List[str]]:
        """Generate a summary using Gemini's native API."""
        cfg = config or {}
        
        prompt = (
            f"{self.prompt_manager.get_system_prompt()}\n\n"
            f"{self.prompt_manager.get_user_prompt(content)}"
        )
        
        # Import GenerateContentConfig
        
        
        # Create config object with required parameters
        gemini_config = types.GenerateContentConfig(
            temperature=cfg.get("temperature", self.temperature),
            max_output_tokens=cfg.get("max_tokens", self.max_tokens),
        )
        
        # Use the async client with the correct parameter structure
        response = await self.async_client.models.generate_content(
            model=cfg.get("model", self.model),
            contents=prompt,
            config=gemini_config
        )
        
        try:
            result = json.loads(response.text)
            return result["summary"], result["keywords"]
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback handling
            return str(response.text), []

    async def batch_generate_summaries(
        self,
        contents: List[str],
        config: Optional[ModelConfig] = None
    ) -> List[tuple[str, List[str]]]:
        """Generate summaries for multiple contents in parallel."""
        return [
            await self.generate_summary(content, config)
            for content in contents
        ]

    @property
    def model_info(self) -> Dict[str, str]:
        return {
            "provider": "Google",
            "model": self.model
        }

class GeminiEmailSummarizer(OpenAIEmailSummarizer):
    """Email summarizer implementation using Gemini's API via OpenAI compatibility layer."""
    
    def __init__(
        self,
        api_key: str,
        model: ProviderModel = ProviderModel.default_for_provider(SummarizerProvider.GOOGLE),
        batch_threshold: int = 10,
        max_batch_size: int = 50,
        timeout: float = 30.0,
        prompt_version: PromptVersion = PromptVersion.latest()
    ):
        prompt_manager = GeminiPromptManager(prompt_version=prompt_version)
        backend = GeminiBackend(
            api_key=api_key,
            prompt_manager=prompt_manager,
            model=model,
        )
        super().__init__(
            api_key=api_key,
            model=model,
            batch_threshold=batch_threshold,
            max_batch_size=max_batch_size,
            timeout=timeout,
            prompt_version=prompt_version
        )
        self._backend = backend
        self._prompt_manager = prompt_manager

    def create_summary(
        self,
        email_id: str,
        summary_text: str,
        keywords: List[str]
    ) -> SummarySchema:
        """Create a SummarySchema from processing results with Gemini model info."""
        return SummarySchema(
            email_id=email_id,
            summary_text=summary_text,
            keywords=keywords,
            generated_at=datetime.now(timezone.utc),
            model_info={
                "provider": "Google",
                "model": self._backend.model
            }
        )
        