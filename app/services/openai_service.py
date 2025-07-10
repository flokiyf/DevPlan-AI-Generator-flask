# -*- coding: utf-8 -*-
"""
Service OpenAI pour DevPlan AI Generator.
Gère la communication avec l'API OpenAI pour la génération de plans de développement.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import OpenAI avec gestion d'erreur
try:
    from openai import OpenAI
    from openai.types import ChatCompletion
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    
from ..utils.exceptions import OpenAIException, ConfigurationException

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service pour interagir avec l'API OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, organization: Optional[str] = None):
        """
        Initialise le service OpenAI.
        
        Args:
            api_key: Clé API OpenAI (optionnel, utilise la variable d'environnement)
            organization: ID de l'organisation OpenAI (optionnel)
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationException(
                "Le package OpenAI n'est pas installé. "
                "Installez-le avec: pip install openai"
            )
        
        self.logger = logging.getLogger(__name__)
        
        # Configuration de l'API
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.organization = organization or os.getenv('OPENAI_ORGANIZATION')
        
        if not self.api_key:
            raise ConfigurationException(
                "Clé API OpenAI non configurée. "
                "Définissez la variable d'environnement OPENAI_API_KEY"
            )
        
        # Initialisation du client OpenAI
        try:
            client_config = {'api_key': self.api_key}
            if self.organization:
                client_config['organization'] = self.organization
                
            self.client = OpenAI(**client_config)
            self.logger.info("Client OpenAI initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation client OpenAI: {str(e)}")
            raise ConfigurationException(f"Impossible d'initialiser le client OpenAI: {str(e)}")
        
        # Configuration par défaut
        self.default_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Teste la connexion à l'API OpenAI.
        
        Returns:
            Dict contenant les informations de test
            
        Raises:
            OpenAIException: En cas d'erreur de connexion
        """
        try:
            self.logger.info("Test de connexion OpenAI...")
            
            # Test simple avec un prompt minimal
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant de test."},
                    {"role": "user", "content": "Réponds simplement 'OK' pour confirmer la connexion."}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            # Extraire la réponse
            response_text = response.choices[0].message.content.strip()
            
            # Informations de test
            test_info = {
                'status': 'success',
                'model_used': response.model,
                'response': response_text,
                'tokens_used': response.usage.total_tokens if response.usage else 0,
                'timestamp': datetime.now().isoformat(),
                'api_key_configured': bool(self.api_key),
                'organization_configured': bool(self.organization)
            }
            
            self.logger.info(f"Test connexion réussi - Modèle: {response.model}")
            return test_info
            
        except Exception as e:
            error_msg = f"Erreur de connexion OpenAI: {str(e)}"
            self.logger.error(error_msg)
            raise OpenAIException(error_msg)
    
    def generate_development_plan(self, project_data: Dict[str, Any]) -> str:
        """
        Génère un plan de développement basé sur les données du projet.
        
        Args:
            project_data: Dictionnaire contenant les informations du projet
            
        Returns:
            str: Plan de développement généré
            
        Raises:
            OpenAIException: En cas d'erreur de génération
        """
        try:
            self.logger.info(f"Génération plan pour projet: {project_data.get('project_type', 'unknown')}")
            
            # Construction du prompt
            prompt = self._build_development_plan_prompt(project_data)
            
            # Appel à l'API OpenAI
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un expert en développement full-stack et architecture logicielle. "
                                 "Tu génères des plans de développement détaillés, structurés et pratiques."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extraction du contenu
            plan_content = response.choices[0].message.content.strip()
            
            # Log des statistiques
            if response.usage:
                self.logger.info(
                    f"Plan généré - Tokens utilisés: {response.usage.total_tokens} "
                    f"(prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})"
                )
            
            return plan_content
            
        except Exception as e:
            error_msg = f"Erreur génération plan: {str(e)}"
            self.logger.error(error_msg)
            raise OpenAIException(error_msg)
    
    def _build_development_plan_prompt(self, project_data: Dict[str, Any]) -> str:
        """
        Construit le prompt pour la génération du plan de développement.
        
        Args:
            project_data: Données du projet
            
        Returns:
            str: Prompt formaté
        """
        project_type = project_data.get('project_type', 'application web')
        description = project_data.get('description', 'Pas de description fournie')
        requirements = project_data.get('requirements', '')
        scale = project_data.get('scale', 'medium')
        
        # Technologies préférées
        frontend_pref = project_data.get('frontend_preference', '')
        backend_pref = project_data.get('backend_preference', '')
        database_pref = project_data.get('database_preference', '')
        
        prompt = f"""
Génère un plan de développement détaillé pour le projet suivant :

**Type de projet :** {project_type}
**Description :** {description}
**Échelle :** {scale}
**Exigences particulières :** {requirements if requirements else 'Aucune'}

**Préférences technologiques :**
- Frontend : {frontend_pref if frontend_pref else 'Aucune préférence'}
- Backend : {backend_pref if backend_pref else 'Aucune préférence'}  
- Base de données : {database_pref if database_pref else 'Aucune préférence'}

Fournis un plan structuré incluant :

## 1. Analyse du Projet
- Objectifs principaux
- Public cible
- Contraintes identifiées

## 2. Architecture Recommandée
- Stack technologique justifiée
- Architecture système (frontend, backend, base de données)
- Patterns de conception recommandés

## 3. Plan de Développement
- Phases de développement (avec durées estimées)
- Tâches prioritaires pour chaque phase
- Jalons importants

## 4. Considérations Techniques
- Sécurité
- Performance
- Scalabilité
- Maintenance

## 5. Recommandations
- Outils de développement
- Bonnes pratiques
- Points d'attention

Le plan doit être pratique, réalisable et adapté au niveau de complexité du projet.
Utilise des estimations réalistes et propose des alternatives si nécessaire.
"""
        
        return prompt.strip()
    
    def generate_technical_documentation(self, project_data: Dict[str, Any], 
                                       plan_content: str) -> str:
        """
        Génère de la documentation technique basée sur le plan.
        
        Args:
            project_data: Données du projet
            plan_content: Contenu du plan de développement
            
        Returns:
            str: Documentation technique générée
        """
        try:
            prompt = f"""
Basé sur ce plan de développement :

{plan_content}

Génère une documentation technique détaillée incluant :

## Structure du Projet
- Organisation des dossiers et fichiers
- Conventions de nommage

## Guide d'Installation
- Prérequis système
- Instructions d'installation pas à pas
- Configuration de l'environnement

## API Documentation
- Endpoints principaux
- Formats de données
- Exemples d'utilisation

## Guide de Déploiement
- Processus de déploiement
- Configuration production
- Monitoring et maintenance

La documentation doit être claire, complète et facile à suivre.
"""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en documentation technique. "
                                 "Tu crées des documentations claires et complètes."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.5  # Plus déterministe pour la documentation
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = f"Erreur génération documentation: {str(e)}"
            self.logger.error(error_msg)
            raise OpenAIException(error_msg)
    
    def get_technology_recommendations(self, project_type: str, 
                                     requirements: List[str]) -> Dict[str, Any]:
        """
        Obtient des recommandations technologiques spécifiques.
        
        Args:
            project_type: Type de projet
            requirements: Liste des exigences
            
        Returns:
            Dict: Recommandations technologiques
        """
        try:
            requirements_text = ', '.join(requirements) if requirements else 'Aucune exigence spécifique'
            
            prompt = f"""
Pour un projet de type "{project_type}" avec les exigences suivantes : {requirements_text}

Fournis des recommandations technologiques structurées :

## Frontend
- Framework recommandé avec justification
- Alternatives viables
- Bibliothèques utiles

## Backend  
- Langage/framework recommandé
- Architecture (REST, GraphQL, etc.)
- Outils et bibliothèques

## Base de Données
- Type de base de données recommandé
- Justification du choix
- Considérations de performance

## DevOps & Déploiement
- Outils de CI/CD
- Plateformes de déploiement
- Monitoring et logging

## Sécurité
- Mesures de sécurité essentielles
- Outils de sécurité recommandés

Fournis des justifications concrètes pour chaque recommandation.
"""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un architecte logiciel expert. "
                                 "Tu fournis des recommandations technologiques précises et justifiées."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.6
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'recommendations': content,
                'model_used': response.model,
                'tokens_used': response.usage.total_tokens if response.usage else 0,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Erreur recommandations technologiques: {str(e)}"
            self.logger.error(error_msg)
            raise OpenAIException(error_msg)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle configuré.
        
        Returns:
            Dict: Informations du modèle
        """
        return {
            'model': self.default_model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'api_key_configured': bool(self.api_key),
            'organization_configured': bool(self.organization)
        } 