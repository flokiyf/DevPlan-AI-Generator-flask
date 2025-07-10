"""
Exceptions personnalisées pour DevPlan AI Generator
"""


class DevPlanException(Exception):
    """Exception de base pour l'application DevPlan"""
    
    def __init__(self, message="Une erreur s'est produite dans DevPlan", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OpenAIException(DevPlanException):
    """Exception spécifique aux erreurs OpenAI"""
    
    def __init__(self, message="Erreur lors de la communication avec OpenAI", code="OPENAI_ERROR", details=None):
        self.details = details
        super().__init__(message, code)


class ValidationException(DevPlanException):
    """Exception spécifique aux erreurs de validation"""
    
    def __init__(self, message="Erreur de validation des données", code="VALIDATION_ERROR", field=None):
        self.field = field
        super().__init__(message, code)


class ConfigurationException(DevPlanException):
    """Exception spécifique aux erreurs de configuration"""
    
    def __init__(self, message="Erreur de configuration", code="CONFIG_ERROR", setting=None):
        self.setting = setting
        super().__init__(message, code)


class APIException(DevPlanException):
    """Exception spécifique aux erreurs d'API"""
    
    def __init__(self, message="Erreur API", code="API_ERROR", status_code=None):
        self.status_code = status_code
        super().__init__(message, code) 