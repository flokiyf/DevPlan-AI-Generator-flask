# -*- coding: utf-8 -*-
"""
Service de validation pour DevPlan AI Generator.
Valide et nettoie les données d'entrée pour la génération de plans.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from html import escape
import bleach

from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ValidationService:
    """Service de validation et sanitisation des données."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration de validation
        self.max_description_length = 2000
        self.max_requirements_length = 1000
        self.min_description_length = 10
        
        # Types de projets valides
        self.valid_project_types = {
            'ecommerce', 'blog', 'saas', 'portfolio', 'api', 
            'mobile', 'dashboard', 'custom'
        }
        
        # Échelles valides
        self.valid_scales = {'small', 'medium', 'large'}
        
        # Technologies supportées
        self.supported_technologies = {
            'frontend': {
                'react', 'vue', 'angular', 'nextjs', 'svelte', 
                'vanilla', 'jquery', 'bootstrap'
            },
            'backend': {
                'nodejs', 'python', 'php', 'java', 'csharp', 
                'ruby', 'go', 'rust'
            },
            'database': {
                'postgresql', 'mysql', 'mongodb', 'sqlite', 
                'redis', 'elasticsearch'
            }
        }
        
        # Mots-clés de sécurité à détecter
        self.security_keywords = {
            'paiement', 'payment', 'authentification', 'auth', 'login',
            'sécurité', 'security', 'encryption', 'chiffrement',
            'données personnelles', 'gdpr', 'rgpd'
        }
        
        # Configuration de sanitisation HTML
        self.allowed_tags = ['b', 'i', 'em', 'strong', 'u']
        self.allowed_attributes = {}
    
    def validate_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide et nettoie les données d'un projet.
        
        Args:
            data: Dictionnaire contenant les données du projet
            
        Returns:
            Dict contenant:
                - is_valid: bool
                - errors: List[str]
                - cleaned_data: Dict[str, Any]
                - warnings: List[str]
        """
        try:
            self.logger.info("Validation des données projet")
            
            errors = []
            warnings = []
            cleaned_data = {}
            
            # Validation du type de projet
            project_type_result = self._validate_project_type(data.get('project_type'))
            if project_type_result['error']:
                errors.append(project_type_result['error'])
            else:
                cleaned_data['project_type'] = project_type_result['value']
            
            # Validation de la description
            description_result = self._validate_description(data.get('description'))
            if description_result['error']:
                errors.append(description_result['error'])
            else:
                cleaned_data['description'] = description_result['value']
                if description_result['warning']:
                    warnings.append(description_result['warning'])
            
            # Validation de l'échelle
            scale_result = self._validate_scale(data.get('scale'))
            if scale_result['error']:
                errors.append(scale_result['error'])
            else:
                cleaned_data['scale'] = scale_result['value']
            
            # Validation des exigences
            requirements_result = self._validate_requirements(data.get('requirements'))
            if requirements_result['error']:
                errors.append(requirements_result['error'])
            else:
                cleaned_data['requirements'] = requirements_result['value']
                if requirements_result['security_detected']:
                    warnings.append("Exigences de sécurité détectées - Assurez-vous de les prioriser")
            
            # Validation des préférences technologiques
            tech_result = self._validate_technology_preferences(data)
            cleaned_data.update(tech_result['cleaned_data'])
            warnings.extend(tech_result['warnings'])
            
            # Validation des données optionnelles
            optional_result = self._validate_optional_fields(data)
            cleaned_data.update(optional_result)
            
            # Validation croisée
            cross_validation_result = self._cross_validate(cleaned_data)
            warnings.extend(cross_validation_result['warnings'])
            
            # Résultat final
            is_valid = len(errors) == 0
            
            result = {
                'is_valid': is_valid,
                'errors': errors,
                'cleaned_data': cleaned_data,
                'warnings': warnings
            }
            
            self.logger.info(f"Validation terminée - Valide: {is_valid}, Erreurs: {len(errors)}, Avertissements: {len(warnings)}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur validation: {str(e)}")
            raise ValidationException(f"Erreur lors de la validation: {str(e)}")
    
    def _validate_project_type(self, project_type: Any) -> Dict[str, Any]:
        """Valide le type de projet."""
        if not project_type:
            return {
                'error': 'Le type de projet est obligatoire',
                'value': None
            }
        
        project_type = str(project_type).lower().strip()
        
        if project_type not in self.valid_project_types:
            return {
                'error': f'Type de projet invalide. Types supportés: {", ".join(self.valid_project_types)}',
                'value': None
            }
        
        return {
            'error': None,
            'value': project_type
        }
    
    def _validate_description(self, description: Any) -> Dict[str, Any]:
        """Valide la description du projet."""
        if not description:
            return {
                'error': 'La description du projet est obligatoire',
                'value': None,
                'warning': None
            }
        
        description = str(description).strip()
        
        # Vérification de la longueur
        if len(description) < self.min_description_length:
            return {
                'error': f'La description doit contenir au moins {self.min_description_length} caractères',
                'value': None,
                'warning': None
            }
        
        if len(description) > self.max_description_length:
            return {
                'error': f'La description ne peut pas dépasser {self.max_description_length} caractères',
                'value': None,
                'warning': None
            }
        
        # Sanitisation
        cleaned_description = self._sanitize_text(description)
        
        warning = None
        if len(cleaned_description) < 50:
            warning = "Description courte - Plus de détails amélioreront la qualité du plan généré"
        
        return {
            'error': None,
            'value': cleaned_description,
            'warning': warning
        }
    
    def _validate_scale(self, scale: Any) -> Dict[str, Any]:
        """Valide l'échelle du projet."""
        if not scale:
            # Valeur par défaut
            return {
                'error': None,
                'value': 'medium'
            }
        
        scale = str(scale).lower().strip()
        
        if scale not in self.valid_scales:
            return {
                'error': f'Échelle invalide. Échelles supportées: {", ".join(self.valid_scales)}',
                'value': None
            }
        
        return {
            'error': None,
            'value': scale
        }
    
    def _validate_requirements(self, requirements: Any) -> Dict[str, Any]:
        """Valide les exigences du projet."""
        if not requirements:
            return {
                'error': None,
                'value': '',
                'security_detected': False
            }
        
        requirements = str(requirements).strip()
        
        if len(requirements) > self.max_requirements_length:
            return {
                'error': f'Les exigences ne peuvent pas dépasser {self.max_requirements_length} caractères',
                'value': None,
                'security_detected': False
            }
        
        # Sanitisation
        cleaned_requirements = self._sanitize_text(requirements)
        
        # Détection d'exigences de sécurité
        security_detected = self._detect_security_requirements(cleaned_requirements)
        
        return {
            'error': None,
            'value': cleaned_requirements,
            'security_detected': security_detected
        }
    
    def _validate_technology_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les préférences technologiques."""
        cleaned_data = {}
        warnings = []
        
        # Frontend
        frontend_pref = data.get('frontend_preference')
        if frontend_pref:
            frontend_pref = str(frontend_pref).lower().strip()
            if frontend_pref in self.supported_technologies['frontend']:
                cleaned_data['frontend_preference'] = frontend_pref
            else:
                warnings.append(f"Technologie frontend '{frontend_pref}' non reconnue - Sera traitée comme préférence personnalisée")
                cleaned_data['frontend_preference'] = frontend_pref
        else:
            cleaned_data['frontend_preference'] = ''
        
        # Backend
        backend_pref = data.get('backend_preference')
        if backend_pref:
            backend_pref = str(backend_pref).lower().strip()
            if backend_pref in self.supported_technologies['backend']:
                cleaned_data['backend_preference'] = backend_pref
            else:
                warnings.append(f"Technologie backend '{backend_pref}' non reconnue - Sera traitée comme préférence personnalisée")
                cleaned_data['backend_preference'] = backend_pref
        else:
            cleaned_data['backend_preference'] = ''
        
        # Database
        database_pref = data.get('database_preference')
        if database_pref:
            database_pref = str(database_pref).lower().strip()
            if database_pref in self.supported_technologies['database']:
                cleaned_data['database_preference'] = database_pref
            else:
                warnings.append(f"Base de données '{database_pref}' non reconnue - Sera traitée comme préférence personnalisée")
                cleaned_data['database_preference'] = database_pref
        else:
            cleaned_data['database_preference'] = ''
        
        return {
            'cleaned_data': cleaned_data,
            'warnings': warnings
        }
    
    def _validate_optional_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les champs optionnels."""
        cleaned_data = {}
        
        # Budget (si fourni)
        budget = data.get('budget')
        if budget:
            try:
                budget_value = float(str(budget).replace(',', '.'))
                if budget_value < 0:
                    cleaned_data['budget'] = 0
                else:
                    cleaned_data['budget'] = budget_value
            except (ValueError, TypeError):
                cleaned_data['budget'] = None
        else:
            cleaned_data['budget'] = None
        
        # Timeline (si fourni)
        timeline = data.get('timeline')
        if timeline:
            try:
                timeline_value = int(str(timeline))
                if timeline_value < 1:
                    cleaned_data['timeline'] = 1
                elif timeline_value > 365:
                    cleaned_data['timeline'] = 365
                else:
                    cleaned_data['timeline'] = timeline_value
            except (ValueError, TypeError):
                cleaned_data['timeline'] = None
        else:
            cleaned_data['timeline'] = None
        
        # Team size (si fourni)
        team_size = data.get('team_size')
        if team_size:
            try:
                team_size_value = int(str(team_size))
                if team_size_value < 1:
                    cleaned_data['team_size'] = 1
                elif team_size_value > 50:
                    cleaned_data['team_size'] = 50
                else:
                    cleaned_data['team_size'] = team_size_value
            except (ValueError, TypeError):
                cleaned_data['team_size'] = None
        else:
            cleaned_data['team_size'] = None
        
        return cleaned_data
    
    def _cross_validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une validation croisée des données."""
        warnings = []
        
        # Vérifier cohérence échelle/complexité
        project_type = data.get('project_type')
        scale = data.get('scale')
        
        if project_type == 'api' and scale == 'large':
            warnings.append("Une API de grande échelle peut nécessiter une architecture microservices")
        
        if project_type == 'ecommerce' and scale == 'small':
            warnings.append("Un projet e-commerce est généralement d'échelle moyenne ou grande")
        
        # Vérifier cohérence technologies/projet
        frontend_pref = data.get('frontend_preference')
        if project_type == 'api' and frontend_pref:
            warnings.append("Une API n'a généralement pas besoin de technologie frontend")
        
        # Vérifier exigences vs échelle
        requirements = data.get('requirements', '').lower()
        if 'temps réel' in requirements and scale == 'small':
            warnings.append("Les fonctionnalités temps réel augmentent la complexité du projet")
        
        return {
            'warnings': warnings
        }
    
    def _sanitize_text(self, text: str) -> str:
        """Nettoie et sécurise un texte."""
        if not text:
            return ''
        
        # Suppression des caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Nettoyage HTML
        text = bleach.clean(text, tags=self.allowed_tags, attributes=self.allowed_attributes, strip=True)
        
        # Échappement des caractères spéciaux restants
        text = escape(text)
        
        # Normalisation des espaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _detect_security_requirements(self, requirements: str) -> bool:
        """Détecte si les exigences contiennent des éléments de sécurité."""
        requirements_lower = requirements.lower()
        
        for keyword in self.security_keywords:
            if keyword in requirements_lower:
                return True
        
        return False
    
    def validate_tech_stack(self, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide une stack technologique complète.
        
        Args:
            tech_stack: Dictionnaire contenant la stack technologique
            
        Returns:
            Dict: Résultat de validation
        """
        try:
            errors = []
            warnings = []
            cleaned_stack = {}
            
            # Validation frontend
            if 'frontend' in tech_stack:
                frontend = str(tech_stack['frontend']).lower().strip()
                if frontend in self.supported_technologies['frontend']:
                    cleaned_stack['frontend'] = frontend
                else:
                    warnings.append(f"Technologie frontend '{frontend}' non standard")
                    cleaned_stack['frontend'] = frontend
            
            # Validation backend
            if 'backend' in tech_stack:
                backend = str(tech_stack['backend']).lower().strip()
                if backend in self.supported_technologies['backend']:
                    cleaned_stack['backend'] = backend
                else:
                    warnings.append(f"Technologie backend '{backend}' non standard")
                    cleaned_stack['backend'] = backend
            
            # Validation database
            if 'database' in tech_stack:
                database = str(tech_stack['database']).lower().strip()
                if database in self.supported_technologies['database']:
                    cleaned_stack['database'] = database
                else:
                    warnings.append(f"Base de données '{database}' non standard")
                    cleaned_stack['database'] = database
            
            # Validation de cohérence
            if 'frontend' in cleaned_stack and 'backend' in cleaned_stack:
                frontend = cleaned_stack['frontend']
                backend = cleaned_stack['backend']
                
                # Vérifications de compatibilité
                if frontend == 'nextjs' and backend != 'nodejs':
                    warnings.append("Next.js fonctionne mieux avec Node.js comme backend")
                
                if frontend == 'angular' and backend == 'php':
                    warnings.append("Angular avec PHP n'est pas une combinaison optimale")
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'cleaned_stack': cleaned_stack
            }
            
        except Exception as e:
            self.logger.error(f"Erreur validation tech stack: {str(e)}")
            raise ValidationException(f"Erreur validation tech stack: {str(e)}")
    
    def validate_openai_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide la configuration OpenAI.
        
        Args:
            config: Configuration OpenAI
            
        Returns:
            Dict: Résultat de validation
        """
        errors = []
        warnings = []
        
        # Validation de la clé API
        api_key = config.get('api_key')
        if not api_key:
            errors.append("Clé API OpenAI requise")
        elif not isinstance(api_key, str) or len(api_key.strip()) < 10:
            errors.append("Clé API OpenAI invalide")
        elif not api_key.startswith('sk-'):
            warnings.append("La clé API ne semble pas être au format OpenAI standard")
        
        # Validation du modèle
        model = config.get('model', 'gpt-3.5-turbo')
        valid_models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview', 'gpt-4o', 'gpt-4o-mini']
        if model not in valid_models:
            warnings.append(f"Modèle '{model}' non standard. Modèles recommandés: {', '.join(valid_models)}")
        
        # Validation température
        temperature = config.get('temperature', 0.7)
        try:
            temp_float = float(temperature)
            if temp_float < 0 or temp_float > 2:
                errors.append("La température doit être entre 0 et 2")
        except (ValueError, TypeError):
            errors.append("Température invalide")
        
        # Validation max_tokens
        max_tokens = config.get('max_tokens', 2000)
        try:
            tokens_int = int(max_tokens)
            if tokens_int < 1 or tokens_int > 8000:
                warnings.append("Le nombre de tokens devrait être entre 1 et 8000")
        except (ValueError, TypeError):
            errors.append("Nombre de tokens invalide")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """
        Génère un résumé textuel de la validation.
        
        Args:
            validation_result: Résultat de validation
            
        Returns:
            str: Résumé textuel
        """
        summary_parts = []
        
        if validation_result['is_valid']:
            summary_parts.append("✅ Validation réussie")
        else:
            summary_parts.append("❌ Validation échouée")
            summary_parts.append(f"Erreurs: {len(validation_result['errors'])}")
        
        if validation_result.get('warnings'):
            summary_parts.append(f"Avertissements: {len(validation_result['warnings'])}")
        
        return " - ".join(summary_parts) 