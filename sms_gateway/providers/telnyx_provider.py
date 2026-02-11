"""Telnyx SMS provider implementation."""
import httpx
from .base import BaseProvider, SMSMessage, SMSResult

class TelnyxProvider(BaseProvider):
    """Telnyx SMS/MMS provider with Canadian number support."""
    
    BASE_URL = "https://api.telnyx.com/v2"
    
    def __init__(self, api_key: str, messaging_profile_id: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.messaging_profile_id = messaging_profile_id
    
    async def send(self, message: SMSMessage) -> SMSResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": message.to,
            "text": message.body,
            "type": "SMS",
        }
        if message.from_number:
            payload["from"] = message.from_number
        if self.messaging_profile_id:
            payload["messaging_profile_id"] = self.messaging_profile_id
        if message.media_url:
            payload["media_urls"] = [message.media_url]
            payload["type"] = "MMS"
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/messages",
                headers=headers,
                json=payload
            )
            
            if resp.status_code in (200, 201):
                body = resp.json().get("data", {})
                return SMSResult(
                    success=True,
                    message_id=body.get("id"),
                    provider="telnyx",
                    status=body.get("to", [{}])[0].get("status", "queued") if body.get("to") else "queued",
                )
            else:
                error_msg = resp.json().get("errors", [{}])[0].get("detail", resp.text) if resp.status_code != 500 else resp.text
                return SMSResult(
                    success=False,
                    provider="telnyx",
                    error=error_msg,
                )
    
    async def get_status(self, message_id: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/messages/{message_id}", headers=headers)
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("to", [{}])[0].get("status", "unknown")
            return "error"
    
    async def get_balance(self) -> float:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/balance", headers=headers)
            if resp.status_code == 200:
                return float(resp.json().get("data", {}).get("balance", 0))
            return 0.0

    async def buy_number(self, area_code: str = "437") -> dict:
        """Purchase a Canadian phone number by area code."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Search available numbers
        async with httpx.AsyncClient() as client:
            search_resp = await client.get(
                f"{self.BASE_URL}/available_phone_numbers",
                headers=headers,
                params={
                    "filter[country_code]": "CA",
                    "filter[national_destination_code]": area_code,
                    "filter[features]": "sms",
                    "filter[limit]": 1
                }
            )
            
            if search_resp.status_code == 200:
                numbers = search_resp.json().get("data", [])
                if numbers:
                    phone = numbers[0].get("phone_number")
                    # Order the number
                    order_resp = await client.post(
                        f"{self.BASE_URL}/number_orders",
                        headers=headers,
                        json={
                            "phone_numbers": [{"phone_number": phone}],
                            "messaging_profile_id": self.messaging_profile_id
                        }
                    )
                    return order_resp.json()
            return {"error": "No numbers available"}