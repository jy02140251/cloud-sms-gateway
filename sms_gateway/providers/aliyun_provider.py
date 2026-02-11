"""Aliyun (China) SMS provider integration."""

import hashlib
import hmac
import base64
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from urllib.parse import quote_plus

from .base import BaseSMSProvider, SMSResult, DeliveryStatus

logger = logging.getLogger(__name__)


class AliyunProvider(BaseSMSProvider):
    """SMS provider implementation for Aliyun (China) SMS service."""

    API_ENDPOINT = "https://dysmsapi.aliyuncs.com"

    def __init__(self, config: Dict[str, Any]):
        super().__init__("aliyun", config)
        self.access_key_id = config["access_key_id"]
        self.access_key_secret = config["access_key_secret"]
        self.sign_name = config.get("sign_name", "")
        self.template_code = config.get("template_code", "")
        self._session = None

    def _sign_request(self, params: Dict[str, str]) -> str:
        sorted_params = sorted(params.items())
        query_string = "&".join(
            f"{quote_plus(k)}={quote_plus(v)}" for k, v in sorted_params
        )
        string_to_sign = f"GET&%2F&{quote_plus(query_string)}"
        signing_key = f"{self.access_key_secret}&"
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("utf-8")
        return signature

    def _build_common_params(self) -> Dict[str, str]:
        return {
            "Format": "JSON",
            "Version": "2017-05-25",
            "AccessKeyId": self.access_key_id,
            "SignatureMethod": "HMAC-SHA1",
            "SignatureVersion": "1.0",
            "SignatureNonce": str(uuid.uuid4()),
            "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    async def send(self, phone_number: str, message: str) -> SMSResult:
        logger.info(f"Sending SMS via Aliyun to {phone_number}")
        try:
            import aiohttp
            if self._session is None:
                self._session = aiohttp.ClientSession()

            params = self._build_common_params()
            params.update({
                "Action": "SendSms",
                "PhoneNumbers": phone_number,
                "SignName": self.sign_name,
                "TemplateCode": self.template_code,
                "TemplateParam": json.dumps({"message": message}),
            })
            params["Signature"] = self._sign_request(params)

            async with self._session.get(
                self.API_ENDPOINT, params=params, timeout=self._timeout
            ) as resp:
                data = await resp.json()
                if data.get("Code") == "OK":
                    return SMSResult(
                        provider=self.name,
                        message_id=data.get("BizId", ""),
                        status=DeliveryStatus.SENT,
                        phone_number=phone_number,
                        raw_response=data,
                    )
                return SMSResult(
                    provider=self.name,
                    message_id="",
                    status=DeliveryStatus.FAILED,
                    phone_number=phone_number,
                    error_message=data.get("Message", "Unknown error"),
                    raw_response=data,
                )
        except Exception as e:
            logger.error(f"Aliyun send failed: {e}")
            return SMSResult(
                provider=self.name,
                message_id="",
                status=DeliveryStatus.FAILED,
                phone_number=phone_number,
                error_message=str(e),
            )

    async def check_balance(self) -> float:
        logger.warning("Aliyun SMS does not provide balance API")
        return -1.0

    async def query_status(self, message_id: str) -> DeliveryStatus:
        logger.info(f"Querying Aliyun delivery status for {message_id}")
        return DeliveryStatus.PENDING