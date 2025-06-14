# Core
from typing import List, Optional, Dict, TypeVar
from datetime import datetime, timezone
import asyncio
import json
import sys

from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
# internal
from app.services.summarization.base import AdaptiveSummarizer
from app.services.summarization.types import ModelBackend, ModelConfig
from app.models import EmailSchema, SummarySchema
from app.utils.config import ProviderModel, SummarizerProvider
from app.services.summarization.prompts import PromptManager
from .prompts import OpenRouterPromptManager
from app.utils.config import PromptVersion
from app.utils.helpers import get_logger

class OpenRouterBackend(ModelBackend):
    """OpenRouter implementation that delegates model routing to the provider."""
    
    def __init__(
        self,
        api_key: str,
        prompt_manager: PromptManager,
        temperature: float = 0.3,
        max_tokens: int = 150,
    ):
        self.logger = get_logger(self.__class__.__name__, 'service')
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key            
        )
        self.prompt_manager = prompt_manager
        self.temperature = temperature
        self.max_tokens = max_tokens

    @retry(
        retry=retry_if_exception_type((
            RateLimitError,
            APITimeoutError,
            APIError,
        )),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3)
    )
    async def generate_summary(
        self,
        content: str,
        config: Optional[ModelConfig] = None
    ) -> tuple[str, List[str]]:
        """Generate a summary, letting OpenRouter handle model selection."""
        cfg = config or {}
        
        messages = [
            {
                "role": "system", 
                "content": self.prompt_manager.get_system_prompt()
            },
            {
                "role": "user", 
                "content": self.prompt_manager.get_user_prompt(content)
            }
        ]
        
        # Log the request payload for diagnostics
        request_payload = {
            "messages": messages,
            "temperature": cfg.get("temperature", self.temperature),
            "max_tokens": cfg.get("max_tokens", self.max_tokens),
            "models": ProviderModel.get_openrouter_fallbacks(),
            "route": "fallback"
        }
        self.logger.info(f"Sending request to OpenRouter: {json.dumps(request_payload, indent=2)}")

        try:
            # Let OpenRouter select the model from the provided list
            response = await self.client.chat.completions.create(
                model=ProviderModel.get_openrouter_fallbacks()[0], # Required by SDK, OR will use list below
                messages=messages,
                temperature=cfg.get("temperature", self.temperature),
                max_tokens=cfg.get("max_tokens", self.max_tokens),
                response_format=self.prompt_manager.get_response_format(),
                extra_body={
                    "models": ProviderModel.get_openrouter_fallbacks(),
                    "route": "fallback" # Ensures it tries models in order
                }
            )
        except APIError as e:
            self.logger.error(f"OpenRouter API request failed with status code {e.status_code}.")
            if e.body:
                self.logger.error(f"Error response body: {e.body}")
            raise # Re-raise the exception to be handled by the retry decorator or calling service

        # Parse the response
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get("summary", ""), result.get("keywords", [])
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback handling if JSON parsing fails
            self.logger.warning(f"Failed to parse JSON. Response: {response.choices[0].message.content if response.choices else 'empty'}. Error: {e}")
            summary = response.choices[0].message.content
            return summary.strip(), []

    async def batch_generate_summaries(
        self,
        contents: List[str],
        config: Optional[ModelConfig] = None
    ) -> List[tuple[str, List[str]]]:
        """Generate summaries for multiple emails."""
        # Implement concurrent processing with rate limiting
        semaphore = asyncio.Semaphore(5)  # Limit concurrent API calls
        
        async def _process_with_semaphore(content: str) -> tuple[str, List[str]]:
            async with semaphore:
                return await self.generate_summary(content, config)
        
        return await asyncio.gather(
            *[_process_with_semaphore(content) for content in contents]
        )

    @property
    def model_info(self) -> Dict[str, str]:
        return {
            "provider": "OpenRouter",
            "model": "auto" # Model is selected by OpenRouter
        }

class OpenRouterEmailSummarizer(AdaptiveSummarizer[EmailSchema]):
    """Email summarizer implementation using OpenRouter's API."""
    
    def __init__(
        self,
        api_key: str,
        batch_threshold: int = 10,
        max_batch_size: int = 50,
        timeout: float = 30.0,
        prompt_version: PromptVersion = PromptVersion.latest(),
    ):
        prompt_manager = OpenRouterPromptManager(prompt_version=prompt_version)
        backend = OpenRouterBackend(
            api_key=api_key,
            prompt_manager=prompt_manager,
        )
        super().__init__(
            model_backend=backend,
            prompt_manager=prompt_manager,
            batch_threshold=batch_threshold,
            max_batch_size=max_batch_size,
            timeout=timeout
        )

    async def prepare_content(self, email: EmailSchema) -> str:
        """Transform EmailSchema into processable content."""
        return (
            f"From: {email.sender}\n" 
            f"To: {', '.join(email.recipients)}\n"
            f"Subject: {email.subject}\n"
            f"Date: {email.received_at}\n\n"
            f"Body:\n{email.body}"
        )

    def create_summary(
        self,
        email_id: str,
        summary_text: str,
        keywords: List[str],
        google_id: str
    ) -> SummarySchema:
        """Create a SummarySchema from processing results."""
        return SummarySchema(
            email_id=email_id,
            summary_text=summary_text,
            keywords=keywords,
            generated_at=datetime.now(timezone.utc),
            model_info=self._backend.model_info,
            google_id=google_id
        )