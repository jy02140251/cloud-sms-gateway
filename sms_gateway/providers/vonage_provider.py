"""Vonage (Nexmo) SMS provider implementation."""
import httpx
from .base import BaseProvider, SMSMessage, SMSResult

class VonageProvider(BaseProvider):
    """Vonage SMS provider."""
    
    BASE_URL = "https://rest.nexmo.com"
    
    def __init__(self, api_key: str, api_secret: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_secret = api_secret
    
    async def send(self, message: SMSMessage) -> SMSResult:
        payload = {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "to": message.to,
            "text": message.body,
        }
        if message.from_number:
            payload["from"] = message.from_number
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.BASE_URL}/sms/json", json=payload)
            
            if resp.status_code == 200:
                data = resp.json()
                msg_data = data.get("messages", [{}])[0]
                status = msg_data.get("status", "1")
                
                if status == "0":
                    return SMSResult(
                        success=True,
                        message_id=msg_data.get("message-id"),
                        provider="vonage",
                        status="sent",
                        price=float(msg_data.get("message-price", 0)),
                    )
                else:
                    return SMSResult(
                        success=False,
                        provider="vonage",
                        error=msg_data.get("error-text", "Unknown error"),
                    )
            return SMSResult(success=False, provider="vonage", error=resp.text)
    
    async def get_status(self, message_id: str) -> str:
        return "unknown"  # Vonage uses webhooks for delivery receipts
    
    async def get_balance(self) -> float:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/account/get-balance",
                params={"api_key": self.api_key, "api_secret": self.api_secret}
            )
            if resp.status_code == 200:
                return float(resp.json().get("value", 0))
            return 0.0