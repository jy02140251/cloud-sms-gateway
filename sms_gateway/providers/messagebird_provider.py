"""MessageBird SMS provider implementation."""
import httpx
from .base import BaseProvider, SMSMessage, SMSResult

class MessageBirdProvider(BaseProvider):
    """MessageBird SMS provider."""
    
    BASE_URL = "https://rest.messagebird.com"
    
    async def send(self, message: SMSMessage) -> SMSResult:
        headers = {
            "Authorization": f"AccessKey {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "recipients": [message.to],
            "body": message.body,
        }
        if message.from_number:
            payload["originator"] = message.from_number
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.BASE_URL}/messages", headers=headers, json=payload)
            
            if resp.status_code in (200, 201):
                body = resp.json()
                return SMSResult(
                    success=True,
                    message_id=body.get("id"),
                    provider="messagebird",
                    status="sent",
                )
            return SMSResult(success=False, provider="messagebird", error=resp.text)
    
    async def get_status(self, message_id: str) -> str:
        headers = {"Authorization": f"AccessKey {self.api_key}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/messages/{message_id}", headers=headers)
            if resp.status_code == 200:
                return resp.json().get("status", "unknown")
            return "error"
    
    async def get_balance(self) -> float:
        headers = {"Authorization": f"AccessKey {self.api_key}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/balance", headers=headers)
            if resp.status_code == 200:
                return float(resp.json().get("amount", 0))
            return 0.0