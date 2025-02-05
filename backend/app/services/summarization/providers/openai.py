from typing import List, Optional, Dict
from datetime import datetime, timezone
import asyncio
import json
from openai import (
    RateLimitError,
    APITimeoutError,
    APIError,
    AsyncOpenAI
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
# internal
from ..base import AdaptiveSummarizer
from ..types import ModelBackend, ModelConfig
from app.models import EmailSchema, SummarySchema

class OpenAIBackend(ModelBackend):
    """OpenAI implementation of the ModelBackend protocol."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 150
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def _create_system_prompt(self) -> str:
        return (
            "You are a precise email summarizer. Create a concise, factual "
            "single-sentence summary that captures the key message or request. "
            "Additionally, extract 3-5 key topics or themes. "
            "Format your response as JSON with 'summary' and 'keywords' fields."
        )
        
    def _create_user_prompt(self, content: str) -> str:
        return (
            "Please summarize this email and extract key topics.\n\n"
            f"Email Content:\n{content}"
        )

    @retry(
        retry=retry_if_exception_type((
            RateLimitError,
            APITimeoutError,
            APIError
        )),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3)
    )
    async def generate_summary(
        self,
        content: str,
        config: Optional[ModelConfig] = None
    ) -> tuple[str, List[str]]:
        """Generate a summary for a single email."""
        cfg = config or {}
        
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
            {"role": "user", "content": self._create_user_prompt(content)}
        ]
        
        response = await self.client.chat.completions.create(
            model=cfg.get("model", self.model),
            messages=messages,
            temperature=cfg.get("temperature", self.temperature),
            max_tokens=cfg.get("max_tokens", self.max_tokens),
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        try:
            result = json.loads(response.choices[0].message.content)
            return result["summary"], result["keywords"]
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback handling if JSON parsing fails
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

class OpenAIEmailSummarizer(AdaptiveSummarizer[EmailSchema]):
    """Email summarizer implementation using OpenAI's API."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        batch_threshold: int = 10,
        max_batch_size: int = 50,
        timeout: float = 30.0
    ):
        backend = OpenAIBackend(
            api_key=api_key,
            model=model
        )
        super().__init__(
            model_backend=backend,
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
        keywords: List[str]
    ) -> SummarySchema:
        """Create a SummarySchema from processing results."""
        return SummarySchema(
            email_id=email_id,
            summary_text=summary_text,
            keywords=keywords,
            generated_at=datetime.now(timezone.utc)
        )