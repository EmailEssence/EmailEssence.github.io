from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.services.summarization.prompts import(
    BasePromptManager,
    PromptTemplate,
    EMAIL_SUMMARY_USER_PROMPT,
    PromptManager,
    EMAIL_SUMMARY_SYSTEM_PROMPT
)
from app.utils.config import PromptVersion

# New OpenRouter-specific system prompt
OPENROUTER_SYSTEM_PROMPT_TEMPLATE = """You are a precise email summarizer. Your task is to analyze the user's email and provide a response in valid JSON format.

You must respond with a JSON object containing exactly these fields:
- "summary": A concise, factual single-sentence summary capturing the key message or request
- "keywords": An array of 3-5 key topics or themes extracted from the email

Example response format:
{
  "summary": "The sender is requesting a meeting to discuss the quarterly budget review.",
  "keywords": ["meeting", "quarterly", "budget", "review", "discussion"]
}

IMPORTANT: Respond only with a valid JSON object. Do not add any explanatory text or wrap the JSON in markdown code blocks."""

EMAIL_SUMMARY_OPENROUTER_SYSTEM_PROMPT = PromptTemplate(
    version=PromptVersion.V1,
    template=OPENROUTER_SYSTEM_PROMPT_TEMPLATE,
    metadata={}
)

@dataclass
class OpenRouterPromptTemplate(PromptTemplate):
    """
    OpenRouter-specific prompt template with basic JSON response format.
    """
    
    def get_response_format(self) -> Dict[str, Any]:
        """
        Return the basic JSON response format supported by most OpenRouter models.
        """
        return {
            "type": "json_object"
        }

# Simplified prompt template
EMAIL_SUMMARY_OPENROUTER_PROMPT = OpenRouterPromptTemplate(
    version=PromptVersion.V1,
    template=EMAIL_SUMMARY_OPENROUTER_SYSTEM_PROMPT.template,
    metadata={}
)

@dataclass
class OpenRouterPromptManager(PromptManager):
    """OpenRouter-specific prompt management, mirroring OpenAI's structure."""
    prompt_version: PromptVersion = PromptVersion.latest()
    
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        return OPENROUTER_SYSTEM_PROMPT_TEMPLATE
    
    def get_user_prompt(self, content: str, version: Optional[PromptVersion] = None) -> str:
        return EMAIL_SUMMARY_USER_PROMPT.template.format(content=content)
    
    def get_response_format(self, version: Optional[PromptVersion] = None) -> Dict[str, Any]:
        """
        Return the basic JSON response format supported by most OpenRouter models.
        """
        return {"type": "json_object"}