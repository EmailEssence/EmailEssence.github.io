from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from datetime import datetime, timezone
import asyncio
import logging

from app.models import SummarySchema, EmailSchema
from .types import ModelBackend, ProcessingStrategy, SummaryMetrics, ModelConfig

""" ( Pipeline )
    EmailSchema → content preparation → LLM processing → SummarySchema
"""

# Constrain generic type to EmailSchema
T = TypeVar('T', bound=EmailSchema)
class AdaptiveSummarizer(ABC, Generic[T]):
    """
    Abstract base class for adaptive email summarization.
    
    Implements intelligent batch processing with performance monitoring and
    automatic strategy selection based on input characteristics.
    """
    def __init__(
        self,
        model_backend: ModelBackend,
        batch_threshold: int = 10,
        max_batch_size: int = 50,
        timeout: float = 30.0,
        model_config: Optional[ModelConfig] = None
    ):
        self._backend = model_backend
        self.batch_threshold = batch_threshold
        self.max_batch_size = max_batch_size
        self.timeout = timeout
        self.model_config = model_config or {}
        self._metrics: List[SummaryMetrics] = []
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def prepare_content(self, email: T) -> str:
        """
        Transform EmailSchema into processable content.
        Args:
            email: Strongly typed EmailSchema instance
        Returns:
            str: Formatted content for model processing
        Note: Implementation must handle all required EmailSchema fields
        """
        raise NotImplementedError

    @abstractmethod
    def create_summary(
        self,
        email_id: str,
        summary_text: str,
        keywords: List[str]
    ) -> SummarySchema:
        """Create a SummarySchema instance from processing results"""
        raise NotImplementedError

    async def process_single(self, email: T) -> SummarySchema:
        """Process a single item through the model pipeline"""
        if not hasattr(email, 'email_id'): # is this an email ? ;)
            raise ValueError(f"Item of type {type(email)} must have email_id attribute")

        content = await self.prepare_content(email)
        start_time = datetime.now(timezone.utc)
        
        try:
            summary_text, keywords = await asyncio.wait_for(
                self._backend.generate_summary(content, self.model_config),
                timeout=self.timeout
            )
            return self.create_summary(email.email_id, summary_text, keywords)
            
        except asyncio.TimeoutError:
            self._logger.error(f"Timeout processing email: {email.email_id}")
            raise
        finally:
            end_time = datetime.now(timezone.utc)
            self._metrics.append(SummaryMetrics(
                processing_time=(end_time - start_time).total_seconds(),
                token_count=len(content.split()),  # Naive token count
                completion_tokens=len(summary_text.split()) if 'summary_text' in locals() else 0,
                total_tokens=len(content.split()) + (len(summary_text.split()) if 'summary_text' in locals() else 0),
                error_count=1 if 'summary_text' not in locals() else 0
            ))

    async def process_batch(self, emails: List[T]) -> List[SummarySchema]:
        """Process a batch of items through the model pipeline"""
        # Validate all items have email_id
        invalid_items = [
            i for i, item in enumerate(emails) 
            if not hasattr(item, 'email_id')
        ]
        if invalid_items:
            raise ValueError(
                f"Items at indices {invalid_items} missing email_id attribute"
            )
        contents = [await self.prepare_content(email) for email in emails]
        start_time = datetime.now(timezone.utc)
        
        try:
            results = await self._backend.batch_generate_summaries(
                contents,
                self.model_config
            )
            
            summaries = []
            for email, (summary_text, keywords) in zip(emails, results):
                email_id = email.email_id
                summary = self.create_summary(email_id, summary_text, keywords)
                summaries.append(summary)
            
            return summaries
            
        finally:
            end_time = datetime.now(timezone.utc)
            success = 'summaries' in locals()
            
            # Pre-compute token counts once
            content_tokens = sum(len(content.split()) for content in contents)
            completion_tokens = (
                sum(len(summary.summary_text.split()) for summary in summaries)
                if success else 0
            )
            
            self._metrics.append(SummaryMetrics(
                processing_time=(end_time - start_time).total_seconds(),
                token_count=content_tokens,
                completion_tokens=completion_tokens,
                total_tokens=content_tokens + completion_tokens,
                batch_size=len(emails),
                error_count=0 if success else 1
            ))

    async def summarize(
        self,
        items: List[T],
        strategy: ProcessingStrategy = ProcessingStrategy.ADAPTIVE,
        custom_batch_size: Optional[int] = None
    ) -> List[SummarySchema]:
        """
        Adaptively summarize items based on the specified strategy.
        
        Args:
            items: List of items to summarize
            strategy: Processing strategy to use
            custom_batch_size: Override default batch size
            
        Returns:
            List[SummarySchema]: Generated summaries
            
        Raises:
            ValueError: If items list is empty
            TimeoutError: If processing exceeds timeout
        """
        if not items:
            raise ValueError("Cannot summarize empty item list")
            
        batch_size = min(
            custom_batch_size or self.batch_threshold,
            self.max_batch_size
        )
        
        match strategy:
            case ProcessingStrategy.SINGLE:
                return [await self.process_single(item) for item in items]
            case ProcessingStrategy.BATCH:
                results = []
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    results.extend(await self.process_batch(batch))
                return results
            case ProcessingStrategy.ADAPTIVE:
                if len(items) < self.batch_threshold:
                    return [await self.process_single(item) for item in items]
                return await self.process_batch(items)

    @property
    def metrics(self) -> List[SummaryMetrics]:
        """Access collected processing metrics"""
        return self._metrics.copy()

    def reset_metrics(self) -> None:
        """Reset collected metrics"""
        self._metrics.clear()