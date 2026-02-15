"""
Notification template engine for SMS Gateway.
Supports variable interpolation, locale-aware formatting, and template validation.
"""

import re
from typing import Dict, Optional, Any
from datetime import datetime


class TemplateError(Exception):
    """Raised when template rendering fails."""
    pass


class NotificationTemplate:
    """SMS notification template with variable substitution."""
    
    VAR_PATTERN = re.compile(r'\{\{(\w+)\}\}')
    MAX_SMS_LENGTH = 160
    
    def __init__(self, name: str, body: str, locale: str = 'en'):
        self.name = name
        self.body = body
        self.locale = locale
        self._validate_syntax()
    
    def _validate_syntax(self) -> None:
        """Check for unclosed variable tags."""
        opens = self.body.count('{{')
        closes = self.body.count('}}')
        if opens != closes:
            raise TemplateError(f"Mismatched braces in template '{self.name}'")
    
    @property
    def variables(self) -> list:
        """Extract all variable names from the template."""
        return self.VAR_PATTERN.findall(self.body)
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render template with provided context variables."""
        missing = set(self.variables) - set(context.keys())
        if missing:
            raise TemplateError(f"Missing variables: {missing}")
        
        result = self.body
        for key, value in context.items():
            result = result.replace('{{' + key + '}}', str(value))
        
        return result
    
    def render_safe(self, context: Dict[str, Any], default: str = '') -> str:
        """Render template, replacing missing variables with default."""
        result = self.body
        for var in self.variables:
            value = context.get(var, default)
            result = result.replace('{{' + var + '}}', str(value))
        return result
    
    @property
    def segment_count(self) -> int:
        """Estimate SMS segment count (without variables filled)."""
        length = len(self.body)
        if length <= self.MAX_SMS_LENGTH:
            return 1
        return (length + 152) // 153  # multipart: 153 chars per segment


class TemplateRegistry:
    """Central registry for managing notification templates."""
    
    def __init__(self):
        self._templates: Dict[str, NotificationTemplate] = {}
    
    def register(self, name: str, body: str, locale: str = 'en') -> None:
        key = f"{name}:{locale}"
        self._templates[key] = NotificationTemplate(name, body, locale)
    
    def get(self, name: str, locale: str = 'en') -> Optional[NotificationTemplate]:
        return self._templates.get(f"{name}:{locale}")
    
    def render(self, name: str, context: Dict[str, Any], locale: str = 'en') -> str:
        tpl = self.get(name, locale)
        if not tpl:
            raise TemplateError(f"Template '{name}' not found for locale '{locale}'")
        return tpl.render(context)
    
    def list_templates(self) -> list:
        return list(self._templates.keys())


# Built-in templates
DEFAULT_TEMPLATES = {
    'verification': 'Your verification code is {{code}}. Valid for {{minutes}} minutes.',
    'welcome': 'Welcome to {{app_name}}, {{user_name}}! Your account is ready.',
    'alert': '[{{severity}}] {{service}}: {{message}}',
    'otp': '{{code}} is your one-time password for {{app_name}}. Do not share.',
}