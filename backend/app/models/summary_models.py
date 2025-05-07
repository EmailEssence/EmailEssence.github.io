from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional, Dict

class SummarySchema(BaseModel):
    """
    Schema for email summaries.
    """
    google_id: str  # Google User ID for consistent user identification
    email_id: str
    summary_text: str
    keywords: List[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_info: Optional[Dict[str, str]] = None
    
    model_config = ConfigDict(frozen=True)  # Using new Pydantic v2 syntax for immutability
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SummarySchema":
        """
        Create a SummarySchema instance from a dictionary.
        
        Args:
            data: Dictionary containing summary data
            
        Returns:
            SummarySchema: New instance
        """
        if isinstance(data, cls):
            return data
        return cls(**data)
    
    def to_dict(self) -> Dict:
        """
        Convert summary to a dictionary for MongoDB storage.
        
        Returns:
            Dict: Dictionary representation of this summary
        """
        return self.model_dump()  # Using Pydantic v2 method