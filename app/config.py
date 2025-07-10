"""
Configuration centralisée pour DevPlan AI Generator Flask Application
"""

import os
from datetime import timedelta


class Config:
    """Configuration de base pour l'application"""
    
    # Configuration Flask de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuration OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_ORGANIZATION = os.environ.get('OPENAI_ORGANIZATION')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Configuration base de données (optionnel)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///devplan.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration export
    EXPORT_FOLDER = os.environ.get('EXPORT_FOLDER', 'exports')
    MAX_EXPORT_SIZE = os.environ.get('MAX_EXPORT_SIZE', '10MB')
    ALLOWED_EXPORT_FORMATS = ['pdf', 'markdown', 'json']
    
    # Configuration application
    APP_NAME = os.environ.get('APP_NAME', 'DevPlan AI Generator')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@devplan.com')
    
    # Configuration sécurité
    CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 heure
    SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Configuration upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Configuration logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    
    # Configuration cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def init_app(app):
        """Initialisation spécifique de la configuration"""
        # Créer les dossiers nécessaires
        os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('logs', exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Configuration OpenAI pour dev
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Configuration BDD pour dev
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///devplan_dev.db')
    
    # Configuration logging pour dev
    LOG_LEVEL = 'DEBUG'
    
    # Configuration sécurité pour dev
    WTF_CSRF_ENABLED = True  # Gardé activé même en dev
    SESSION_COOKIE_SECURE = False
    
    # Configuration cache pour dev
    CACHE_TYPE = 'null'  # Pas de cache en dev
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique pour le développement"""
        Config.init_app(app)
        
        # Configuration spécifique au développement
        import logging
        logging.basicConfig(level=logging.DEBUG)
        app.logger.info("🔧 Configuration développement chargée")


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Configuration sécurité pour production
    SESSION_COOKIE_SECURE = True  # Nécessite HTTPS
    WTF_CSRF_ENABLED = True
    
    # Configuration BDD pour production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'devplan_prod.db')
    
    # Configuration logging pour production
    LOG_LEVEL = 'WARNING'
    
    # Configuration cache pour production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique pour la production"""
        Config.init_app(app)
        
        # Configuration logging pour production
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            'logs/devplan.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.WARNING)
        app.logger.info("🚀 Configuration production chargée")


class TestingConfig(Config):
    """Configuration pour les tests"""
    
    TESTING = True
    DEBUG = False
    FLASK_ENV = 'testing'
    
    # Configuration BDD pour tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # BDD en mémoire
    
    # Configuration sécurité pour tests
    WTF_CSRF_ENABLED = False  # Désactivé pour faciliter les tests
    SECRET_KEY = 'test-secret-key'
    
    # Configuration OpenAI pour tests (mock)
    OPENAI_API_KEY = 'test-key'
    OPENAI_MODEL = 'gpt-3.5-turbo'
    
    # Configuration cache pour tests
    CACHE_TYPE = 'null'
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique pour les tests"""
        Config.init_app(app)
        app.logger.info("🧪 Configuration test chargée")


# Mapping des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 