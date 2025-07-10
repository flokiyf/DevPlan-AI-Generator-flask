"""
Factory pattern pour l'application DevPlan AI Generator Flask
"""

import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect

# Import de la configuration
from .config import Config, DevelopmentConfig, ProductionConfig

# Import des extensions (à implémenter plus tard)
# from .extensions import db, migrate, login_manager

def create_app(config_name='development'):
    """
    Factory function pour créer l'application Flask
    
    Args:
        config_name (str): Nom de la configuration ('development', 'production', 'testing')
    
    Returns:
        Flask: Instance de l'application Flask configurée
    """
    
    # Créer l'instance Flask
    app = Flask(__name__)
    
    # Configuration
    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': Config  # Configuration de base pour les tests
    }
    
    config_class = config_mapping.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    # Configuration du logging
    setup_logging(app)
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Enregistrer les blueprints/routes
    register_blueprints(app)
    
    # Gestionnaires d'erreurs
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    app.logger.info(f"✅ Application DevPlan initialisée en mode {config_name}")
    
    return app

def setup_logging(app):
    """Configure le système de logging"""
    if not app.debug and not app.testing:
        # Configuration logging pour production
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/devplan.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('🚀 DevPlan AI Generator startup')

def init_extensions(app):
    """Initialise les extensions Flask"""
    
    # Protection CSRF
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # À implémenter plus tard :
    # db.init_app(app)
    # migrate.init_app(app, db)
    # login_manager.init_app(app)
    
    app.logger.info("🔧 Extensions initialisées")

def register_blueprints(app):
    """Enregistre les blueprints de routes"""
    
    # Import des routes
    from .routes.main import main_bp
    
    # Enregistrement des blueprints
    app.register_blueprint(main_bp)
    
    app.logger.info("🛣️ Blueprints enregistrés")

def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs personnalisés"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Erreur serveur: {error}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def too_large(error):
        return render_template('errors/413.html'), 413
    
    app.logger.info("❌ Gestionnaires d'erreurs enregistrés")

def register_context_processors(app):
    """Enregistre les context processors pour les templates"""
    
    @app.context_processor
    def inject_config():
        """Injecte des variables de configuration dans tous les templates"""
        return {
            'app_name': app.config.get('APP_NAME', 'DevPlan AI Generator'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
        }
    
    @app.context_processor
    def utility_processor():
        """Injecte des fonctions utilitaires dans les templates"""
        def format_datetime(dt):
            """Formate une date/heure pour l'affichage"""
            if dt is None:
                return ""
            return dt.strftime('%d/%m/%Y à %H:%M')
        
        return dict(format_datetime=format_datetime)
    
    app.logger.info("📝 Context processors enregistrés")

# Import pour éviter les imports circulaires
from flask import render_template 