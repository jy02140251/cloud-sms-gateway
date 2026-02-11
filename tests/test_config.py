"""Tests for configuration management module."""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from sms_gateway.config import GatewayConfig, ProviderConfig


class TestGatewayConfig:
    def test_default_values(self):
        config = GatewayConfig()
        assert config.environment == "development"
        assert config.log_level == "INFO"
        assert config.max_concurrent_sends == 50
        assert config.rate_limit_per_second == 10

    def test_from_env(self):
        with patch.dict(os.environ, {
            "SMS_GATEWAY_ENV": "production",
            "LOG_LEVEL": "DEBUG",
            "MAX_CONCURRENT_SENDS": "100",
        }):
            config = GatewayConfig.from_env()
            assert config.environment == "production"
            assert config.log_level == "DEBUG"
            assert config.max_concurrent_sends == 100

    def test_from_env_defaults(self):
        config = GatewayConfig.from_env()
        assert config.redis_url == "redis://localhost:6379/0"
        assert config.default_provider is None


class TestProviderConfig:
    def test_default_provider_config(self):
        pc = ProviderConfig(name="test_provider")
        assert pc.enabled is True
        assert pc.priority == 0
        assert pc.max_retries == 3
        assert pc.timeout == 30
        assert pc.credentials == {}

    def test_custom_provider_config(self):
        pc = ProviderConfig(
            name="twilio",
            enabled=True,
            priority=1,
            credentials={"sid": "test123"},
        )
        assert pc.name == "twilio"
        assert pc.priority == 1
        assert pc.credentials["sid"] == "test123"