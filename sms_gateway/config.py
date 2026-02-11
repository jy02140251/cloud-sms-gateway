"""Configuration management for SMS Cloud Gateway."""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.json"


@dataclass
class ProviderConfig:
    name: str
    enabled: bool = True
    priority: int = 0
    max_retries: int = 3
    timeout: int = 30
    credentials: Dict[str, str] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayConfig:
    environment: str = "development"
    log_level: str = "INFO"
    max_concurrent_sends: int = 50
    default_provider: Optional[str] = None
    rate_limit_per_second: int = 10
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite:///sms_gateway.db"
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "GatewayConfig":
        """Load configuration from environment variables."""
        config = cls(
            environment=os.getenv("SMS_GATEWAY_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_concurrent_sends=int(os.getenv("MAX_CONCURRENT_SENDS", "50")),
            default_provider=os.getenv("DEFAULT_PROVIDER"),
            rate_limit_per_second=int(os.getenv("RATE_LIMIT_PER_SECOND", "10")),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///sms_gateway.db"),
        )
        logger.info(f"Loaded config for environment: {config.environment}")
        return config

    @classmethod
    def from_file(cls, path: Optional[Path] = None) -> "GatewayConfig":
        """Load configuration from a JSON file."""
        config_path = path or DEFAULT_CONFIG_PATH
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls.from_env()
        with open(config_path) as f:
            data = json.load(f)
        config = cls.from_env()
        for key, value in data.items():
            if key == "providers":
                for pname, pconfig in value.items():
                    config.providers[pname] = ProviderConfig(name=pname, **pconfig)
            elif hasattr(config, key):
                setattr(config, key, value)
        return config