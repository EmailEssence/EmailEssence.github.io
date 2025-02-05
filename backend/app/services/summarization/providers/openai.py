from ..base import AdaptiveSummarizer
from ..types import ModelBackend, ModelConfig
from models import EmailSchema, SummarySchema

from typing import List, Optional, Dict
from datetime import datetime
import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class OpenAIBackend(ModelBackend):
    """
    OpenAI-based implementation of ModelBackend protocol.
    
    Implements both single and batch processing capabilities while
    maintaining consistent API interaction patterns and error handling.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or (
            "You are a precise email summarizer. "
            "Create concise, factual summaries and extract key topics."
        )
        
    @retry(
        retry=retry_if_exception_type((
            openai.RateLimitError,
            openai.APITimeoutError
        )),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3)
    )
    async def generate_summary(
        self,
        content: str,
        config: Optional[Dict[str, any]] = None
    ) -> tuple[str, List[str]]:
        """Generate summary for single email content."""
        cfg = config or {}
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._format_prompt(content)}
        ]
        
        response = await self.client.chat.completions.create(
            model=cfg.get("model", self.model),
            messages=messages,
            temperature=cfg.get("temperature", self.temperature),
            max_tokens=cfg.get("max_tokens", self.max_tokens),
            response_format={ "type": "json_object" }
        )
        
        result = response.choices[0].message.content
        parsed = json.loads(result)
        
        return parsed["summary"], parsed["keywords"]
        
    async def batch_generate_summaries(
        self,
        contents: List[str],
        config: Optional[Dict[str, any]] = None
    ) -> List[tuple[str, List[str]]]:
        """Generate summaries for multiple email contents."""
        # Process in parallel with concurrency control
        semaphore = asyncio.Semaphore(5)  # Limit concurrent API calls
        
        async def _process_with_semaphore(content: str) -> tuple[str, List[str]]:
            async with semaphore:
                return await self.generate_summary(content, config)
        
        return await asyncio.gather(
            *[_process_with_semaphore(content) for content in contents]
        )
        
    def _format_prompt(self, content: str) -> str:
        """Format content into a structured prompt."""
        return (
            "Please summarize this email and extract key topics. "
            "Respond in JSON format with 'summary' and 'keywords' fields.\n\n"
            f"Email Content:\n{content}"
        )