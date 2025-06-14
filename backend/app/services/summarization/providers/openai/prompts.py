# Standard library imports
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Internal imports
from app.services.summarization.prompts import(
    PromptManager,
    EMAIL_SUMMARY_SYSTEM_PROMPT,
    EMAIL_SUMMARY_USER_PROMPT
)
from app.utils.config import PromptVersion

@dataclass
class OpenAIPromptManager(PromptManager):
    """OpenAI-specific prompt management."""
    prompt_version: PromptVersion = PromptVersion.latest()
    
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        return EMAIL_SUMMARY_SYSTEM_PROMPT.template
    
    def get_user_prompt(self, content: str, version: Optional[PromptVersion] = None) -> str:
        return EMAIL_SUMMARY_USER_PROMPT.template.format(content=content)
    
    def get_response_format(self, version: Optional[PromptVersion] = None) -> Dict[str, Any]:
        return EMAIL_SUMMARY_SYSTEM_PROMPT.metadata["response_format"]