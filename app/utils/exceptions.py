# -*- coding: utf-8 -*-
"""
Exceptions personnalisées pour DevPlan AI Generator.
"""


class DevPlanException(Exception):
    """Exception de base pour DevPlan AI Generator."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ValidationException(DevPlanException):
    """Exception levée lors d'erreurs de validation des données."""
    
    def __init__(self, message: str, field: str = None, value=None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class OpenAIException(DevPlanException):
    """Exception levée lors d'erreurs avec l'API OpenAI."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message, "OPENAI_ERROR")
        self.status_code = status_code


class ConfigurationException(DevPlanException):
    """Exception levée lors d'erreurs de configuration."""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key


class APIException(DevPlanException):
    """Exception levée lors d'erreurs d'API."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, "API_ERROR")
        self.status_code = status_code 