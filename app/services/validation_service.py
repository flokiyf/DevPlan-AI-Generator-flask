"""
Service de validation pour DevPlan AI Generator

Ce service gère la validation des données et schémas
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from flask import current_app
from ..utils.exceptions import ValidationException


class ValidationService:
    """Service pour la validation des données et schémas"""
    
    def __init__(self):
        self.required_fields = {
            'project_description': str,
            'requirements': dict
        }
    
    def validate_project_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide les données d'un projet
        
        Args:
            data: Données du projet à valider
            
        Returns:
            Tuple (is_valid, errors_list)
        """
        errors = []
        
        try:
            # Validation des champs requis
            for field, field_type in self.required_fields.items():
                if field not in data:
                    errors.append(f"Le champ '{field}' est requis")
                    continue
                
                if not isinstance(data[field], field_type):
                    errors.append(f"Le champ '{field}' doit être de type {field_type.__name__}")
            
            # Validation spécifique de la description du projet
            if 'project_description' in data:
                desc_errors = self._validate_project_description(data['project_description'])
                errors.extend(desc_errors)
            
            # Validation spécifique des exigences
            if 'requirements' in data:
                req_errors = self._validate_requirements(data['requirements'])
                errors.extend(req_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            current_app.logger.error(f"Erreur validation projet: {str(e)}")
            raise ValidationException(f"Erreur lors de la validation: {str(e)}")
    
    def _validate_project_description(self, description: str) -> List[str]:
        """
        Valide la description du projet
        
        Args:
            description: Description du projet
            
        Returns:
            Liste des erreurs de validation
        """
        errors = []
        
        # Vérification de la longueur
        if len(description.strip()) < 10:
            errors.append("La description du projet doit contenir au moins 10 caractères")
        
        if len(description.strip()) > 5000:
            errors.append("La description du projet ne peut pas dépasser 5000 caractères")
        
        # Vérification du contenu minimal
        description_lower = description.lower()
        required_keywords = ['projet', 'application', 'système', 'plateforme', 'site', 'app']
        
        if not any(keyword in description_lower for keyword in required_keywords):
            errors.append("La description doit mentionner le type de projet (application, système, site, etc.)")
        
        # Vérification des caractères spéciaux dangereux
        dangerous_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'<iframe[^>]*>'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                errors.append("La description contient des éléments non autorisés")
                break
        
        return errors
    
    def _validate_requirements(self, requirements: Dict[str, Any]) -> List[str]:
        """
        Valide les exigences du projet
        
        Args:
            requirements: Dictionnaire des exigences
            
        Returns:
            Liste des erreurs de validation
        """
        errors = []
        
        # Validation de la stack technologique
        if 'technology_stack' in requirements:
            stack_errors = self._validate_technology_stack(requirements['technology_stack'])
            errors.extend(stack_errors)
        
        # Validation de la timeline
        if 'timeline' in requirements:
            timeline_errors = self._validate_timeline(requirements['timeline'])
            errors.extend(timeline_errors)
        
        # Validation de la taille d'équipe
        if 'team_size' in requirements:
            team_errors = self._validate_team_size(requirements['team_size'])
            errors.extend(team_errors)
        
        # Validation du budget
        if 'budget' in requirements:
            budget_errors = self._validate_budget(requirements['budget'])
            errors.extend(budget_errors)
        
        # Validation des fonctionnalités
        if 'features' in requirements:
            features_errors = self._validate_features(requirements['features'])
            errors.extend(features_errors)
        
        return errors
    
    def _validate_technology_stack(self, tech_stack: Any) -> List[str]:
        """Valide la stack technologique"""
        errors = []
        
        if not isinstance(tech_stack, list):
            errors.append("La stack technologique doit être une liste")
            return errors
        
        if len(tech_stack) == 0:
            errors.append("Au moins une technologie doit être spécifiée")
            return errors
        
        # Validation des technologies connues
        known_technologies = {
            'frontend': ['react', 'vue', 'angular', 'svelte', 'vanilla js', 'next.js', 'nuxt.js'],
            'backend': ['node.js', 'python', 'java', 'c#', 'php', 'ruby', 'go', 'rust'],
            'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'firebase'],
            'cloud': ['aws', 'azure', 'gcp', 'heroku', 'vercel', 'netlify']
        }
        
        all_known_tech = []
        for category in known_technologies.values():
            all_known_tech.extend(category)
        
        for tech in tech_stack:
            if not isinstance(tech, str):
                errors.append(f"Chaque technologie doit être une chaîne de caractères")
            elif tech.lower() not in all_known_tech:
                # Warning plutôt qu'erreur pour les technologies non reconnues
                current_app.logger.warning(f"Technologie non reconnue: {tech}")
        
        return errors
    
    def _validate_timeline(self, timeline: Any) -> List[str]:
        """Valide la timeline du projet"""
        errors = []
        
        if not isinstance(timeline, str):
            errors.append("La timeline doit être une chaîne de caractères")
            return errors
        
        # Validation des formats de timeline acceptés
        timeline_patterns = [
            r'^\d+\s*(semaine|semaines|mois|month|months)$',
            r'^\d+\s*-\s*\d+\s*(semaine|semaines|mois|month|months)$',
            r'^(urgent|normal|flexible)$'
        ]
        
        timeline_lower = timeline.lower().strip()
        
        if not any(re.match(pattern, timeline_lower) for pattern in timeline_patterns):
            errors.append("Format de timeline non valide. Exemples: '3 mois', '2-4 semaines', 'urgent'")
        
        return errors
    
    def _validate_team_size(self, team_size: Any) -> List[str]:
        """Valide la taille de l'équipe"""
        errors = []
        
        if isinstance(team_size, str):
            try:
                team_size = int(team_size)
            except ValueError:
                errors.append("La taille d'équipe doit être un nombre")
                return errors
        
        if not isinstance(team_size, int):
            errors.append("La taille d'équipe doit être un nombre entier")
            return errors
        
        if team_size < 1:
            errors.append("La taille d'équipe doit être au moins 1")
        elif team_size > 50:
            errors.append("La taille d'équipe ne peut pas dépasser 50 développeurs")
        
        return errors
    
    def _validate_budget(self, budget: Any) -> List[str]:
        """Valide le budget du projet"""
        errors = []
        
        if not isinstance(budget, str):
            errors.append("Le budget doit être une chaîne de caractères")
            return errors
        
        # Validation des formats de budget
        budget_patterns = [
            r'^\d+k?\$?$',  # 10k, 50000, 100k$
            r'^\d+\s*-\s*\d+k?\$?$',  # 10-50k, 10000-50000$
            r'^(petit|moyen|grand|illimité)$',  # Budget relatif
            r'^\d+\s*(euros?|dollars?|\$|€)$'  # Avec devise
        ]
        
        budget_lower = budget.lower().strip()
        
        if not any(re.match(pattern, budget_lower) for pattern in budget_patterns):
            errors.append("Format de budget non valide. Exemples: '50k$', '10-50k', 'moyen', '100000€'")
        
        return errors
    
    def _validate_features(self, features: Any) -> List[str]:
        """Valide la liste des fonctionnalités"""
        errors = []
        
        if not isinstance(features, list):
            errors.append("Les fonctionnalités doivent être une liste")
            return errors
        
        if len(features) == 0:
            errors.append("Au moins une fonctionnalité doit être spécifiée")
            return errors
        
        for i, feature in enumerate(features):
            if not isinstance(feature, str):
                errors.append(f"La fonctionnalité {i+1} doit être une chaîne de caractères")
            elif len(feature.strip()) < 3:
                errors.append(f"La fonctionnalité {i+1} doit contenir au moins 3 caractères")
            elif len(feature.strip()) > 200:
                errors.append(f"La fonctionnalité {i+1} ne peut pas dépasser 200 caractères")
        
        return errors
    
    def validate_openai_config(self, api_key: str, model: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Valide la configuration OpenAI
        
        Args:
            api_key: Clé API OpenAI
            model: Modèle OpenAI (optionnel)
            
        Returns:
            Tuple (is_valid, errors_list)
        """
        errors = []
        
        # Validation de la clé API
        if not api_key or not isinstance(api_key, str):
            errors.append("La clé API OpenAI est requise")
        else:
            # Validation du format de la clé API
            if not api_key.startswith('sk-'):
                errors.append("La clé API OpenAI doit commencer par 'sk-'")
            elif len(api_key) < 40:
                errors.append("La clé API OpenAI semble trop courte")
        
        # Validation du modèle
        if model:
            supported_models = [
                'gpt-3.5-turbo',
                'gpt-3.5-turbo-16k',
                'gpt-4',
                'gpt-4-32k',
                'gpt-4-turbo-preview'
            ]
            
            if model not in supported_models:
                errors.append(f"Modèle non supporté. Modèles disponibles: {', '.join(supported_models)}")
        
        return len(errors) == 0, errors
    
    def sanitize_input(self, input_data: str) -> str:
        """
        Nettoie et sécurise les données d'entrée
        
        Args:
            input_data: Données à nettoyer
            
        Returns:
            Données nettoyées
        """
        if not isinstance(input_data, str):
            return str(input_data)
        
        # Suppression des balises HTML dangereuses
        dangerous_tags = ['<script', '<iframe', '<object', '<embed', '<form']
        
        cleaned_data = input_data
        for tag in dangerous_tags:
            cleaned_data = re.sub(f'{tag}[^>]*>', '', cleaned_data, flags=re.IGNORECASE)
        
        # Suppression des attributs JavaScript
        js_attributes = ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus']
        for attr in js_attributes:
            cleaned_data = re.sub(f'{attr}\s*=\s*["\'][^"\']*["\']', '', cleaned_data, flags=re.IGNORECASE)
        
        # Limitation de la longueur
        if len(cleaned_data) > 10000:
            cleaned_data = cleaned_data[:10000] + "..."
        
        return cleaned_data.strip() 