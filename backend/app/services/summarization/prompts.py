"""
Prompt management for email summarization.

This module provides abstract base classes and concrete implementations for managing
prompts across different LLM providers.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Optional, Protocol, Dict, Any, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum

# Internal imports
from app.utils.config import PromptVersion

@dataclass
class PromptTemplate:
    """Base class for prompt templates."""
    version: PromptVersion
    template: str
    metadata: Dict[str, Any]

class PromptManager(Protocol):
    """Protocol defining prompt management interface with version handling."""
    prompt_version: PromptVersion = field(
        default=PromptVersion.latest(),
        repr=False,
        compare=True
    )
    
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        """Get system prompt for the specified version.
        Args:
            version: Optional version override
        Returns:
            Formatted system prompt string
        """
        ...
    
    def get_user_prompt(self, content: str, version: Optional[PromptVersion] = None) -> str:
        """Get user prompt for the specified version.
        Args:
            content: Content to be formatted into the prompt
            version: Optional version override
        Returns:
            Formatted user prompt string
        """
        ...

    def get_response_format(self, version: Optional[PromptVersion] = None) -> Dict[str, Any]:
        """Get expected response format for the specified version.
        Args:
            version: Optional version override
        Returns:
            Response format specification
        """
        ...

@dataclass
class BasePromptManager(ABC, PromptManager):
    """Abstract base class implementing version handling for PromptManager protocol."""
    prompt_version: PromptVersion = field(
        default=PromptVersion.latest(),
        repr=False,
        compare=True
    )
    def __init__(self, version: Optional[PromptVersion] = None) -> None:
        """Initialize with optional version override."""
        super().__init__()
        self.prompt_version = version or PromptVersion.latest()

    def __post_init__(self) -> None:
        """Validate and normalize version after initialization."""
        if not isinstance(self.prompt_version, PromptVersion):
            self.prompt_version = PromptVersion(self.prompt_version)
    
    def _get_active_version(self, version: Optional[PromptVersion] = None) -> PromptVersion:
        """Resolve the active version, preferring passed version over instance default.
        
        Args:
            version: Optional version override
        Returns:
            Active PromptVersion to use
        """
        return version or self.prompt_version
    
    @abstractmethod
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        """Get system prompt for the specified version."""
        raise NotImplementedError
    
    @abstractmethod
    def get_user_prompt(self, content: str, version: Optional[PromptVersion] = None) -> str:
        """Get user prompt for the specified version."""
        raise NotImplementedError
    
    @abstractmethod
    def get_response_format(self, version: Optional[PromptVersion] = None) -> Dict[str, Any]:
        """Get expected response format for the specified version."""
        raise NotImplementedError
    
# Core prompt templates
EMAIL_SUMMARY_SYSTEM_PROMPT = PromptTemplate(
    version=PromptVersion.V2,
    template="""You are a precise email summarizer. Your task is to:
1. Create a concise, factual single-sentence summary capturing the key message or request
2. Extract 3-5 key topics or themes as keywords""",
    metadata={
        "description": "System prompt for email summarization with JSON output",
        "response_format": {"type": "json_object"},
        "schema": {
            "summary": "string",
            "keywords": "List[string]"
        }
    }
)

EMAIL_SUMMARY_USER_PROMPT = PromptTemplate(
    version=PromptVersion.V2,
    template="""Please analyze this email and provide a summary and keywords.

Email Content:
{content}""",
    metadata={
        "description": "User prompt for email summarization with JSON format specification",
        "variables": ["content"]
    }
)