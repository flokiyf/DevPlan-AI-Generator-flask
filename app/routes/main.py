"""
Routes principales pour DevPlan AI Generator
"""

from flask import Blueprint, render_template, current_app, jsonify, request, flash
import os
import json
from ..services import OpenAIService, ValidationService, SchemaGenerator
from ..utils.exceptions import OpenAIException, ValidationException, DevPlanException

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

# ==================== ROUTES PR #2 - OpenAI Service ====================

@main_bp.route('/openai-test')
def openai_test():
    """Page de test OpenAI"""
    return render_template('openai_test.html', 
                         title="Test OpenAI",
                         description="Tester la connexion et configuration OpenAI")

@main_bp.route('/api/openai/test', methods=['POST'])
def test_openai_connection():
    """API pour tester la connexion OpenAI"""
    try:
        openai_service = OpenAIService()
        
        # Test de connexion
        result = openai_service.test_connection()
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Connexion OpenAI réussie'
        }), 200
        
    except OpenAIException as e:
        current_app.logger.error(f"Erreur OpenAI: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'openai_error'
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Erreur test OpenAI: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Erreur interne: {str(e)}",
            'type': 'internal_error'
        }), 500

@main_bp.route('/api/openai/generate-plan', methods=['POST'])
def generate_development_plan():
    """API pour générer un plan de développement avec OpenAI"""
    try:
        # Récupérer et valider les données
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        # Validation des données
        validation_service = ValidationService()
        validation_result = validation_service.validate_project_data(data)
        
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'error': 'Données invalides',
                'validation_errors': validation_result['errors']
            }), 400
        
        # Génération du plan avec OpenAI
        openai_service = OpenAIService()
        plan = openai_service.generate_development_plan(validation_result['cleaned_data'])
        
        return jsonify({
            'success': True,
            'data': {
                'content': plan,
                'project_data': validation_result['cleaned_data']
            },
            'message': 'Plan de développement généré avec succès'
        }), 200
        
    except ValidationException as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'validation_error'
        }), 400
        
    except OpenAIException as e:
        current_app.logger.error(f"Erreur OpenAI: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'openai_error'
        }), 500
        
    except Exception as e:
        current_app.logger.error(f"Erreur génération plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Erreur interne: {str(e)}",
            'type': 'internal_error'
        }), 500

@main_bp.route('/api/openai/config', methods=['GET', 'POST'])
def openai_config():
    """API pour la configuration OpenAI"""
    if request.method == 'GET':
        # Retourner la configuration actuelle (sans les secrets)
        return jsonify({
            'success': True,
            'data': {
                'api_key_configured': bool(current_app.config.get('OPENAI_API_KEY')),
                'organization_configured': bool(current_app.config.get('OPENAI_ORGANIZATION')),
                'model': current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo')
            }
        }), 200
    
    elif request.method == 'POST':
        # Mettre à jour la configuration (fonctionnalité future)
        return jsonify({
            'success': False,
            'message': 'Configuration dynamique non implémentée'
        }), 501

# ==================== ROUTES PR #3 - Schema Generator ====================

@main_bp.route('/api/schema/generate-detailed', methods=['POST'])
def generate_detailed_schema():
    """API pour générer un schéma technique détaillé"""
    try:
        # Récupérer et valider les données
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        # Validation des données
        validation_service = ValidationService()
        validation_result = validation_service.validate_project_data(data)
        
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'error': 'Données invalides',
                'validation_errors': validation_result['errors']
            }), 400
        
        # Génération du schéma détaillé
        schema_generator = SchemaGenerator()
        detailed_schema = schema_generator.generate_detailed_schema(validation_result['cleaned_data'])
        
        # Conversion en dictionnaire pour JSON
        schema_dict = schema_generator.export_schema_to_dict(detailed_schema)
        
        return jsonify({
            'success': True,
            'data': {
                'schema': schema_dict,
                'project_data': validation_result['cleaned_data']
            },
            'message': 'Schéma technique généré avec succès'
        }), 200
        
    except ValidationException as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'validation_error'
        }), 400
        
    except DevPlanException as e:
        current_app.logger.error(f"Erreur génération schéma: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'schema_generation_error'
        }), 500
        
    except Exception as e:
        current_app.logger.error(f"Erreur interne génération schéma: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Erreur interne: {str(e)}",
            'type': 'internal_error'
        }), 500

@main_bp.route('/api/schema/analyze-complexity', methods=['POST'])
def analyze_project_complexity():
    """API pour analyser la complexité d'un projet"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        schema_generator = SchemaGenerator()
        complexity = schema_generator.analyze_project_complexity(data)
        
        return jsonify({
            'success': True,
            'data': {
                'complexity': complexity.value,
                'complexity_name': complexity.name
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur analyse complexité: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Erreur: {str(e)}"
        }), 500

@main_bp.route('/api/schema/tech-recommendations', methods=['POST'])
def get_tech_recommendations():
    """API pour obtenir des recommandations technologiques"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        schema_generator = SchemaGenerator()
        complexity = schema_generator.analyze_project_complexity(data)
        recommendations = schema_generator.generate_tech_recommendations(data, complexity)
        
        # Conversion des recommandations en dictionnaire
        recommendations_dict = []
        for rec in recommendations:
            recommendations_dict.append({
                'name': rec.name,
                'category': rec.category.value,
                'version': rec.version,
                'reason': rec.reason,
                'alternatives': rec.alternatives,
                'learning_curve': rec.learning_curve,
                'popularity_score': rec.popularity_score,
                'maintenance_cost': rec.maintenance_cost
            })
        
        return jsonify({
            'success': True,
            'data': {
                'complexity': complexity.value,
                'recommendations': recommendations_dict
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur recommandations tech: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Erreur: {str(e)}"
        }), 500

@main_bp.route('/schema-advanced')
def schema_advanced():
    """Page du générateur de schémas avancés (PR #3)"""
    return render_template('schema_advanced.html', 
                         title="Schémas Avancés",
                         description="Génération de schémas techniques détaillés avec architecture et estimations")

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