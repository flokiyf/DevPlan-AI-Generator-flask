"""
Routes principales pour DevPlan AI Generator
"""

from flask import Blueprint, render_template, current_app, jsonify, request
import os

# Création du blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil principale"""
    return render_template('index.html', 
                         title="Accueil",
                         description="Générateur de schémas full-stack alimenté par l'IA")

@main_bp.route('/about')
def about():
    """Page à propos"""
    return render_template('about.html', 
                         title="À propos",
                         description="Découvrez DevPlan AI Generator")

@main_bp.route('/generator')
def generator():
    """Page du générateur de schémas"""
    return render_template('generator.html', 
                         title="Générateur",
                         description="Créez votre schéma de projet avec l'IA")

@main_bp.route('/health')
def health_check():
    """Endpoint de vérification de l'état de l'application"""
    try:
        # Vérifications de base
        status = {
            'status': 'healthy',
            'app_name': current_app.config.get('APP_NAME'),
            'version': current_app.config.get('APP_VERSION'),
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'debug': current_app.debug,
        }
        
        # Vérification de la configuration OpenAI
        openai_configured = bool(current_app.config.get('OPENAI_API_KEY'))
        status['openai_configured'] = openai_configured
        
        # Vérification des dossiers
        export_folder = current_app.config.get('EXPORT_FOLDER', 'exports')
        export_folder_exists = os.path.exists(export_folder)
        status['export_folder_ready'] = export_folder_exists
        
        # Status global
        if openai_configured and export_folder_exists:
            status['status'] = 'ready'
        elif not openai_configured:
            status['status'] = 'needs_configuration'
            status['message'] = 'OpenAI API key not configured'
        
        return jsonify(status), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur health check: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main_bp.route('/status')
def status():
    """Page de statut de l'application (version HTML du health check)"""
    try:
        # Récupérer les informations de statut
        openai_configured = bool(current_app.config.get('OPENAI_API_KEY'))
        export_folder = current_app.config.get('EXPORT_FOLDER', 'exports')
        export_folder_exists = os.path.exists(export_folder)
        
        status_info = {
            'app_name': current_app.config.get('APP_NAME'),
            'version': current_app.config.get('APP_VERSION'),
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'debug': current_app.debug,
            'openai_configured': openai_configured,
            'export_folder_ready': export_folder_exists,
            'export_folder_path': os.path.abspath(export_folder) if export_folder_exists else None
        }
        
        return render_template('status.html', 
                             title="Statut du système",
                             status=status_info)
        
    except Exception as e:
        current_app.logger.error(f"Erreur page status: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/config')
def config_page():
    """Page de configuration de l'application"""
    return render_template('config.html', 
                         title="Configuration",
                         description="Configurez votre instance DevPlan")

@main_bp.route('/openai-test')
def openai_test():
    """Page de test de la connexion OpenAI"""
    return render_template('openai_test.html')


@main_bp.route('/api/openai/test', methods=['POST'])
def api_openai_test():
    """API pour tester la connexion OpenAI"""
    try:
        from ..services import OpenAIService
        
        # Initialisation du service OpenAI
        openai_service = OpenAIService()
        
        # Test de connexion
        result = openai_service.test_connection()
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur test OpenAI: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erreur lors du test de connexion OpenAI"
        }), 500


@main_bp.route('/api/openai/generate-plan', methods=['POST'])
def api_generate_plan():
    """API pour générer un plan de développement"""
    try:
        from ..services import OpenAIService, ValidationService
        
        # Récupération des données
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Aucune donnée fournie"
            }), 400
        
        # Validation des données
        validation_service = ValidationService()
        is_valid, errors = validation_service.validate_project_data(data)
        
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Données invalides",
                "validation_errors": errors
            }), 400
        
        # Nettoyage des données
        project_description = validation_service.sanitize_input(data.get('project_description', ''))
        requirements = data.get('requirements', {})
        
        # Génération du plan
        openai_service = OpenAIService()
        result = openai_service.generate_development_plan(project_description, requirements)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur génération plan: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erreur lors de la génération du plan"
        }), 500


@main_bp.route('/api/openai/config', methods=['GET', 'POST'])
def api_openai_config():
    """API pour la configuration OpenAI"""
    if request.method == 'GET':
        try:
            from ..services import OpenAIService
            
            openai_service = OpenAIService()
            config_info = openai_service.get_model_info()
            
            return jsonify({
                "success": True,
                "data": config_info
            })
            
        except Exception as e:
            current_app.logger.error(f"Erreur récupération config: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    elif request.method == 'POST':
        try:
            from ..services import ValidationService
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Aucune donnée fournie"
                }), 400
            
            # Validation de la configuration
            validation_service = ValidationService()
            api_key = data.get('api_key', '')
            model = data.get('model', '')
            
            is_valid, errors = validation_service.validate_openai_config(api_key, model)
            
            if not is_valid:
                return jsonify({
                    "success": False,
                    "error": "Configuration invalide",
                    "validation_errors": errors
                }), 400
            
            return jsonify({
                "success": True,
                "message": "Configuration validée avec succès",
                "data": {
                    "api_key_format": "valide",
                    "model": model if model else "gpt-3.5-turbo"
                }
            })
            
        except Exception as e:
            current_app.logger.error(f"Erreur validation config: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

# Routes d'erreur personnalisées pour ce blueprint
@main_bp.app_errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404 personnalisé"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500 personnalisé"""
    current_app.logger.error(f"Erreur interne: {error}")
    return render_template('errors/500.html'), 500 