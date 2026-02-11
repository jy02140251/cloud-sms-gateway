"""Twilio SMS provider implementation."""
import httpx
import base64
from .base import BaseProvider, SMSMessage, SMSResult

class TwilioProvider(BaseProvider):
    """Twilio SMS/MMS provider."""
    
    BASE_URL = "https://api.twilio.com/2010-04-01"
    
    def __init__(self, account_sid: str, auth_token: str, **kwargs):
        super().__init__(api_key=auth_token, **kwargs)
        self.account_sid = account_sid
        self.auth_token = auth_token
    
    async def send(self, message: SMSMessage) -> SMSResult:
        auth = base64.b64encode(f"{self.account_sid}:{self.auth_token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        
        data = {
            "To": message.to,
            "Body": message.body,
        }
        if message.from_number:
            data["From"] = message.from_number
        if message.media_url:
            data["MediaUrl"] = message.media_url
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/Accounts/{self.account_sid}/Messages.json",
                headers=headers,
                data=data
            )
            
            if resp.status_code == 201:
                body = resp.json()
                return SMSResult(
                    success=True,
                    message_id=body.get("sid"),
                    provider="twilio",
                    status=body.get("status", "queued"),
                    price=float(body.get("price", 0) or 0),
                )
            else:
                return SMSResult(
                    success=False,
                    provider="twilio",
                    error=resp.text,
                )
    
    async def get_status(self, message_id: str) -> str:
        auth = base64.b64encode(f"{self.account_sid}:{self.auth_token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/Accounts/{self.account_sid}/Messages/{message_id}.json",
                headers=headers
            )
            if resp.status_code == 200:
                return resp.json().get("status", "unknown")
            return "error"
    
    async def get_balance(self) -> float:
        auth = base64.b64encode(f"{self.account_sid}:{self.auth_token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/Accounts/{self.account_sid}/Balance.json",
                headers=headers
            )
            if resp.status_code == 200:
                return float(resp.json().get("balance", 0))
            return 0.0