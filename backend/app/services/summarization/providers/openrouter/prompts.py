from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.services.summarization.prompts import(
    BasePromptManager,
    PromptTemplate,
    EMAIL_SUMMARY_SYSTEM_PROMPT,
    EMAIL_SUMMARY_USER_PROMPT
)
from app.utils.config import PromptVersion

@dataclass
class OpenRouterPromptTemplate(PromptTemplate):
    """OpenRouter-specific prompt template with JSON schema support."""
    schema_name: str = ""
    schema_properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    strict: bool = True
    
    def get_response_format(self) -> Dict[str, Any]:
        """Generate the OpenRouter-compatible response format."""
        return {
            "type": "json_schema",
            "json_schema": {
                "name": self.schema_name,
                "strict": self.strict,
                "schema": {
                    "type": "object",
                    "properties": self.schema_properties,
                    "required": self.required_fields,
                    "additionalProperties": False
                }
            }
        }

# Example usage:
EMAIL_SUMMARY_OPENROUTER_PROMPT = OpenRouterPromptTemplate(
    version=PromptVersion.V1,
    template=EMAIL_SUMMARY_SYSTEM_PROMPT.template,
    metadata=EMAIL_SUMMARY_SYSTEM_PROMPT.metadata,
    schema_name="email_summary",
    schema_properties={
        "summary": {
            "type": "string",
            "description": "A concise, factual single-sentence summary capturing the key message or request"
        },
        "keywords": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "3-5 key topics or themes extracted from the email"
        }
    },
    required_fields=["summary", "keywords"]
)

@dataclass
class OpenRouterPromptManager(BasePromptManager):
    """OpenRouter-specific prompt management."""
    
    def get_system_prompt(self, version: Optional[PromptVersion] = None) -> str:
        active_version = self._get_active_version(version)
        # Could implement version-specific logic here if needed
        return EMAIL_SUMMARY_SYSTEM_PROMPT.template
    
    def get_user_prompt(self, content: str, version: Optional[PromptVersion] = None) -> str:
        active_version = self._get_active_version(version)
        # Could implement version-specific logic here if needed
        return EMAIL_SUMMARY_USER_PROMPT.template.format(content=content)
    
    def get_response_format(self, version: Optional[PromptVersion] = None) -> Dict[str, Any]:
        active_version = self._get_active_version(version)
        # Could implement version-specific logic here if needed
        return EMAIL_SUMMARY_OPENROUTER_PROMPT.get_response_format()