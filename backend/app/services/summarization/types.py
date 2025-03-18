from typing import Protocol, List, Optional, Dict
from enum import Enum, auto
from pydantic import Field
from dataclasses import dataclass
from datetime import datetime, timezone

ModelConfig = Dict[str, any]

class ProcessingStrategy(Enum):
    SINGLE = auto()
    BATCH = auto()
    ADAPTIVE = auto()

@dataclass
class SummaryMetrics:
    """Performance metrics for summarization operations"""
    processing_time: float
    token_count: int
    completion_tokens: int
    total_tokens: int
    batch_size: Optional[int] = None
    error_count: int = 0
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class ModelBackend(Protocol):
    """Protocol defining required LLM backend capabilities"""
    async def generate_summary(
        self,
        content: str,
        config: Optional[ModelConfig] = None
    ) -> tuple[str, List[str]]: ...
    
    async def batch_generate_summaries(
        self,
        contents: List[str],
        config: Optional[ModelConfig] = None
    ) -> List[tuple[str, List[str]]]: ...

    @property
    def model_info(self) -> Dict[str, str]:
        """Return information about the model being used."""
        ...