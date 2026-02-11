"""Tests for SMS Gateway."""
import pytest
import asyncio
from sms_gateway import SMSGateway
from sms_gateway.providers.base import BaseProvider, SMSMessage, SMSResult

class MockProvider(BaseProvider):
    def __init__(self, should_fail=False):
        super().__init__(api_key="mock")
        self.should_fail = should_fail
        self.sent_messages = []
    
    async def send(self, message: SMSMessage) -> SMSResult:
        if self.should_fail:
            return SMSResult(success=False, error="Mock failure", provider="mock")
        self.sent_messages.append(message)
        return SMSResult(success=True, message_id="mock-123", provider="mock")
    
    async def get_status(self, message_id: str) -> str:
        return "delivered"
    
    async def get_balance(self) -> float:
        return 100.0

@pytest.mark.asyncio
async def test_send_success():
    gw = SMSGateway()
    provider = MockProvider()
    gw.register_provider("mock", provider, primary=True)
    result = await gw.send("+12025551234", "Hello!")
    assert result.success
    assert result.message_id == "mock-123"
    assert len(provider.sent_messages) == 1

@pytest.mark.asyncio
async def test_failover():
    gw = SMSGateway()
    failing = MockProvider(should_fail=True)
    working = MockProvider()
    gw.register_provider("failing", failing, primary=True)
    gw.register_provider("working", working)
    result = await gw.send("+12025551234", "Hello!")
    assert result.success
    assert result.provider == "mock"

@pytest.mark.asyncio
async def test_bulk_send():
    gw = SMSGateway()
    provider = MockProvider()
    gw.register_provider("mock", provider, primary=True)
    messages = [{"to": f"+1202555{i:04d}", "message": f"Msg {i}"} for i in range(10)]
    results = await gw.send_bulk(messages)
    assert len(results) == 10
    assert all(r.success for r in results)

@pytest.mark.asyncio
async def test_stats():
    gw = SMSGateway()
    provider = MockProvider()
    gw.register_provider("mock", provider, primary=True)
    await gw.send("+12025551234", "Test")
    assert gw.stats["sent"] == 1
    assert gw.stats["failed"] == 0