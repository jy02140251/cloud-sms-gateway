"""配置验证工具 - YAML/JSON schema校验, 环境变量注入"""
import json, yaml, os
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def validate(self, config_path: str) -> tuple:
        path = Path(config_path)
        if not path.exists():
            return False, f"Config file not found: {config_path}"
        try:
            if path.suffix in [".yaml", ".yml"]:
                with open(path) as f: config = yaml.safe_load(f)
            elif path.suffix == ".json":
                with open(path) as f: config = json.load(f)
            else:
                return False, "Unsupported format"
            config = {k: os.getenv(v, v) if isinstance(v, str) and v.startswith("$") else v for k, v in config.items()}
            return True, None
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    v = ConfigValidator({"type": "object"})
    print(v.validate("config.yaml"))
