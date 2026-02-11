"""Base provider interface and common data models."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class SMSMessage:
    to: str
    body: str
    from_number: Optional[str] = None
    media_url: Optional[str] = None

@dataclass 
class SMSResult:
    success: bool
    message_id: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    price: Optional[float] = None
    status: str = "unknown"

class BaseProvider(ABC):
    """Abstract base class for SMS providers."""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self._config = kwargs
    
    @abstractmethod
    async def send(self, message: SMSMessage) -> SMSResult:
        """Send a single SMS message."""
        pass
    
    @abstractmethod
    async def get_status(self, message_id: str) -> str:
        """Get delivery status of a message."""
        pass
    
    @abstractmethod
    async def get_balance(self) -> float:
        """Get account balance."""
        pass