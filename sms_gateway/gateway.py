"""Main SMS Gateway class with multi-provider support."""
import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .providers.base import BaseProvider, SMSMessage, SMSResult

logger = logging.getLogger(__name__)

@dataclass
class GatewayConfig:
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    rate_limit_per_second: float = 10.0
    failover_enabled: bool = True

class SMSGateway:
    """Multi-provider SMS gateway with automatic failover and load balancing."""
    
    def __init__(self, config: Optional[GatewayConfig] = None):
        self.config = config or GatewayConfig()
        self._providers: Dict[str, BaseProvider] = {}
        self._primary_provider: Optional[str] = None
        self._stats = {"sent": 0, "failed": 0, "retried": 0}
    
    def register_provider(self, name: str, provider: BaseProvider, primary: bool = False):
        """Register an SMS provider."""
        self._providers[name] = provider
        if primary or not self._primary_provider:
            self._primary_provider = name
        logger.info(f"Registered provider: {name} (primary={primary})")
    
    async def send(self, to: str, message: str, from_number: Optional[str] = None) -> SMSResult:
        """Send an SMS message with automatic failover."""
        msg = SMSMessage(to=to, body=message, from_number=from_number)
        
        providers_to_try = self._get_provider_order()
        last_error = None
        
        for provider_name in providers_to_try:
            provider = self._providers[provider_name]
            try:
                result = await provider.send(msg)
                if result.success:
                    self._stats["sent"] += 1
                    logger.info(f"SMS sent via {provider_name}: {to}")
                    return result
                last_error = result.error
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Provider {provider_name} failed: {e}")
                if self.config.failover_enabled:
                    continue
                raise
        
        self._stats["failed"] += 1
        return SMSResult(success=False, error=last_error or "All providers failed")
    
    async def send_bulk(self, messages: List[Dict], concurrency: int = 10) -> List[SMSResult]:
        """Send multiple SMS messages concurrently."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def _send_one(msg_data):
            async with semaphore:
                return await self.send(**msg_data)
        
        tasks = [_send_one(msg) for msg in messages]
        return await asyncio.gather(*tasks)
    
    def _get_provider_order(self) -> List[str]:
        """Get providers in priority order."""
        if self._primary_provider:
            others = [n for n in self._providers if n != self._primary_provider]
            return [self._primary_provider] + others
        return list(self._providers.keys())
    
    @property
    def stats(self) -> Dict:
        return self._stats.copy()