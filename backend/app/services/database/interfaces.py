from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class IRepository(ABC):
    """Base interface for all repositories"""
    @abstractmethod
    async def find_one(self, query: Dict[str, Any]) -> Optional[BaseModel]:
        pass
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[BaseModel]:
        pass
    
    @abstractmethod
    async def find_many(self, query: Dict[str, Any], limit: int = 100) -> List[BaseModel]:
        pass
    
    @abstractmethod
    async def insert_one(self, model: BaseModel) -> Any:
        pass
    
    @abstractmethod
    async def update_one(self, query: Dict[str, Any], model: BaseModel, upsert: bool = False) -> Any:
        pass
    
    @abstractmethod
    async def delete_one(self, query: Dict[str, Any]) -> Any:
        pass

class IEmailRepository(IRepository):
    """Email repository interface"""
    @abstractmethod
    async def find_by_email_id(self, email_id: str) -> Optional[BaseModel]:
        pass
    
    @abstractmethod
    async def find_unread(self) -> List[BaseModel]:
        pass
    
    @abstractmethod
    async def mark_as_read(self, email_id: str) -> Optional[BaseModel]:
        pass

class IUserRepository(IRepository):
    """User repository interface"""
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[BaseModel]:
        pass
    
    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[BaseModel]:
        pass

class ISummaryRepository(IRepository):
    """Summary repository interface"""
    @abstractmethod
    async def find_by_email_id(self, email_id: str) -> Optional[BaseModel]:
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[BaseModel]:
        pass 

class ITokenRepository(IRepository):
    """Token repository interface"""
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[BaseModel]:
        pass
    
    @abstractmethod
    async def find_by_token(self, token: str) -> Optional[BaseModel]:
        pass
    
    
