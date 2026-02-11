"""Example: Send SMS using Cloud SMS Gateway."""
import asyncio
from sms_gateway import SMSGateway
from sms_gateway.providers import TelnyxProvider, TwilioProvider

async def main():
    # Initialize gateway
    gateway = SMSGateway()
    
    # Register Telnyx as primary (cheapest for Canadian numbers)
    telnyx = TelnyxProvider(
        api_key="YOUR_TELNYX_API_KEY",
        messaging_profile_id="YOUR_PROFILE_ID"
    )
    gateway.register_provider("telnyx", telnyx, primary=True)
    
    # Register Twilio as fallback
    twilio = TwilioProvider(
        account_sid="YOUR_TWILIO_SID",
        auth_token="YOUR_TWILIO_TOKEN"
    )
    gateway.register_provider("twilio", twilio)
    
    # Send a single message
    result = await gateway.send(
        to="+12025551234",
        message="Hello from Cloud SMS Gateway!",
        from_number="+14377846365"  # Canadian number
    )
    print(f"Sent: {result.success}, ID: {result.message_id}")
    
    # Send bulk messages
    messages = [
        {"to": "+12025551234", "message": "Hello!", "from_number": "+14377846365"},
        {"to": "+12025555678", "message": "Hi there!", "from_number": "+14377847068"},
    ]
    results = await gateway.send_bulk(messages, concurrency=5)
    print(f"Bulk sent: {sum(1 for r in results if r.success)}/{len(results)} successful")

if __name__ == "__main__":
    asyncio.run(main())