"""Phone number pool manager for one-to-one target assignment."""
import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class NumberStatus(Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    COOLDOWN = "cooldown"
    DISABLED = "disabled"

@dataclass
class PhoneNumber:
    number: str
    provider: str
    status: NumberStatus = NumberStatus.AVAILABLE
    assigned_target: Optional[str] = None
    assigned_task_id: Optional[str] = None
    last_used: Optional[datetime] = None
    daily_send_count: int = 0
    total_send_count: int = 0

class NumberPool:
    """Manages a pool of phone numbers for SMS sending."""
    
    def __init__(self, daily_limit: int = 20, cooldown_hours: int = 24):
        self._numbers: Dict[str, PhoneNumber] = {}
        self.daily_limit = daily_limit
        self.cooldown_hours = cooldown_hours
        self._lock = asyncio.Lock()
    
    def add_number(self, number: str, provider: str):
        """Add a phone number to the pool."""
        self._numbers[number] = PhoneNumber(number=number, provider=provider)
        logger.info(f"Added number to pool: {number} ({provider})")
    
    def add_numbers_bulk(self, numbers: List[Dict[str, str]]):
        """Add multiple numbers at once."""
        for n in numbers:
            self.add_number(n["number"], n["provider"])
    
    async def assign_number(self, target: str, task_id: str = None) -> Optional[str]:
        """Assign an available number to a target."""
        async with self._lock:
            # Check if target already has an assigned number
            for num in self._numbers.values():
                if num.assigned_target == target and num.status == NumberStatus.ASSIGNED:
                    return num.number
            
            # Find available number
            for num in self._numbers.values():
                if num.status == NumberStatus.AVAILABLE and num.daily_send_count < self.daily_limit:
                    num.status = NumberStatus.ASSIGNED
                    num.assigned_target = target
                    num.assigned_task_id = task_id
                    num.last_used = datetime.utcnow()
                    num.daily_send_count += 1
                    num.total_send_count += 1
                    logger.info(f"Assigned {num.number} -> {target}")
                    return num.number
            
            logger.warning(f"No available numbers for target {target}")
            return None
    
    async def release_number(self, number: str, cooldown: bool = True):
        """Release a number back to the pool."""
        async with self._lock:
            if number in self._numbers:
                num = self._numbers[number]
                if cooldown:
                    num.status = NumberStatus.COOLDOWN
                else:
                    num.status = NumberStatus.AVAILABLE
                num.assigned_target = None
                num.assigned_task_id = None
    
    async def assign_batch(self, targets: List[str], task_id: str = None) -> Dict[str, str]:
        """Assign numbers to multiple targets (one-to-one)."""
        assignments = {}
        for target in targets:
            number = await self.assign_number(target, task_id)
            if number:
                assignments[target] = number
            else:
                break
        return assignments
    
    def reset_daily_counts(self):
        """Reset daily send counts for all numbers."""
        for num in self._numbers.values():
            num.daily_send_count = 0
            if num.status == NumberStatus.COOLDOWN:
                num.status = NumberStatus.AVAILABLE
    
    @property
    def available_count(self) -> int:
        return sum(1 for n in self._numbers.values() if n.status == NumberStatus.AVAILABLE)
    
    @property
    def stats(self) -> Dict:
        status_counts = {}
        for num in self._numbers.values():
            status_counts[num.status.value] = status_counts.get(num.status.value, 0) + 1
        return {
            "total": len(self._numbers),
            **status_counts,
            "daily_limit": self.daily_limit,
        }