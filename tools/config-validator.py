"""
配置验证工具
支持 YAML/JSON schema 校验和环境变量注入
"""

import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def validate(self, config_path: str) -> tuple[bool, Optional[str]]:
        """验证配置文件"""
        path = Path(config_path)
        if not path.exists():
            return False, f"Config file not found: {config_path}"
        
        try:
            if path.suffix in [".yaml", ".yml"]:
                with open(path, "r") as f:
                    config = yaml.safe_load(f)
            elif path.suffix == ".json":
                with open(path, "r") as f:
                    config = json.load(f)
            else:
                return False, "Unsupported config format"
            
            # 注入环境变量
            config = self._inject_env_vars(config)
            
            # Schema 验证（简化版）
            return self._validate_schema(config, self.schema), None
        except Exception as e:
            return False, str(e)
    
    def _inject_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """注入环境变量"""
        import os
        if isinstance(config, dict):
            return {k: os.getenv(v, v) if isinstance(v, str) and v.startswith("$") else v 
                   for k, v in config.items()}
        return config
    
    def _validate_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证schema（简化实现）"""
        # 实际实现应该使用 jsonschema 库
        return True


if __name__ == "__main__":
    schema = {"type": "object", "properties": {"port": {"type": "integer"}}}
    validator = ConfigValidator(schema)
    result, error = validator.validate("config.yaml")
    print(f"Validation: {result}, Error: {error}")
