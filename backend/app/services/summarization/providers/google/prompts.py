from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from app.services.summarization.prompts import(
    PromptManager,
    EMAIL_SUMMARY_SYSTEM_PROMPT,
    EMAIL_SUMMARY_USER_PROMPT
)
from app.utils.config import PromptVersion
from app.services.summarization.prompts import PromptTemplate

@dataclass
class GeminiPromptManager(PromptManager):
    """Gemini-specific prompt management."""
    prompt_version: PromptVersion = PromptVersion.latest()
    
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        """Get system prompt for use in GenerateContentConfig."""
        return EMAIL_SUMMARY_SYSTEM_PROMPT.template
    
    def get_user_prompt(self, content: str, version: Optional[PromptVersion] = None) -> str:
        """Get user prompt for content generation."""
        return EMAIL_SUMMARY_USER_PROMPT.template.format(content=content)
    
    def get_response_format(self, version: Optional[PromptVersion] = None) -> Dict[str, Any]:
        """Get response format specification including schema and MIME type."""
        return {
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A concise, factual single-sentence summary"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 5,
                        "description": "Key topics or themes from the email"
                    }
                },
                "required": ["summary", "keywords"]
            }
        }

# Core prompt templates
EMAIL_SUMMARY_SYSTEM_PROMPT = PromptTemplate(
    version=PromptVersion.V2,
    template="""You are a precise email summarizer. Your task is to:
1. Create a concise, factual single-sentence summary capturing the key message or request
2. Extract 3-5 key topics or themes as keywords""",
    metadata={
        "description": "System prompt for email summarization with JSON output",
        "response_format": {
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                }
            }

        }
    }
)

EMAIL_SUMMARY_USER_PROMPT = PromptTemplate(
    version=PromptVersion.V2,
    template="""Please analyze this email:

{content}""",
    metadata={
        "description": "User prompt for email summarization",
        "variables": ["content"]
    }
)